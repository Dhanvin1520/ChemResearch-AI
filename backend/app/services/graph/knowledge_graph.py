from typing import Optional
from app.models.database import get_db


class KnowledgeGraph:
    def __init__(self):
        pass

    @property
    def db(self):
        return get_db()

    def initialize_schema(self):
        db = self.db
        db.graph_papers.create_index("paper_id", unique=True)
        db.graph_molecules.create_index("name", unique=True)
        db.graph_reactions.create_index("name", unique=True)

    def add_paper(self, paper_data: dict) -> dict:
        self.db.graph_papers.update_one(
            {"paper_id": paper_data["paper_id"]},
            {"$set": {
                "title": paper_data.get("title", ""),
                "year": paper_data.get("year"),
                "doi": paper_data.get("doi"),
                "authors": paper_data.get("authors", []),
                "journal": paper_data.get("journal"),
            }},
            upsert=True
        )
        return paper_data

    def add_molecule(self, name: str, smiles: Optional[str] = None, properties: Optional[dict] = None) -> dict:
        props = properties or {}
        self.db.graph_molecules.update_one(
            {"name": name},
            {"$set": {
                "smiles": smiles,
                "molecular_weight": props.get("molecular_weight"),
                "formula": props.get("molecular_formula"),
            }},
            upsert=True
        )
        return {"name": name}

    def add_reaction(self, name: str, reaction_type: str, paper_id: int, conditions: Optional[dict] = None) -> dict:
        cond = conditions or {}
        self.db.graph_reactions.update_one(
            {"name": name},
            {"$set": {
                "reaction_type": reaction_type,
                "paper_id": paper_id,
                "catalyst": cond.get("catalyst"),
                "solvent": cond.get("solvent"),
                "temperature": cond.get("temperature"),
                "yield_value": cond.get("yield_value"),
            }},
            upsert=True
        )
        return {"name": name}

    def link_paper_molecule(self, paper_id: int, molecule_name: str) -> dict:
        self.db.graph_papers.update_one(
            {"paper_id": paper_id},
            {"$addToSet": {"mentions_molecules": molecule_name}}
        )
        return {}

    def link_reaction_product(self, reaction_name: str, product_name: str) -> dict:
        self.db.graph_reactions.update_one(
            {"name": reaction_name},
            {"$addToSet": {"produces": product_name}}
        )
        return {}

    def find_reactions_by_catalyst(self, catalyst_name: str) -> list[dict]:
        reactions = list(self.db.graph_reactions.find({"catalyst": catalyst_name}))
        results = []
        for r in reactions:
            paper = self.db.graph_papers.find_one({"paper_id": r.get("paper_id")})
            if paper:
                results.append({
                    "reaction": r["name"],
                    "reaction_type": r.get("reaction_type"),
                    "temperature": r.get("temperature"),
                    "yield_value": r.get("yield_value"),
                    "paper_title": paper.get("title"),
                    "year": paper.get("year"),
                    "doi": paper.get("doi")
                })
        results.sort(key=lambda x: x.get("year") or 0, reverse=True)
        return results

    def find_reactions_for_molecule(self, molecule_name: str) -> list[dict]:
        reactions = list(self.db.graph_reactions.find({"produces": molecule_name}))
        results = []
        for r in reactions:
            paper = self.db.graph_papers.find_one({"paper_id": r.get("paper_id")})
            if paper:
                results.append({
                    "reaction": r["name"],
                    "reaction_type": r.get("reaction_type"),
                    "catalyst": r.get("catalyst"),
                    "solvent": r.get("solvent"),
                    "temperature": r.get("temperature"),
                    "yield_value": r.get("yield_value"),
                    "paper_title": paper.get("title"),
                    "year": paper.get("year")
                })
        results.sort(key=lambda x: x.get("year") or 0, reverse=True)
        return results

    def find_papers_for_molecule(self, molecule_name: str) -> list[dict]:
        papers = list(self.db.graph_papers.find({"mentions_molecules": molecule_name}))
        results = []
        for p in papers:
            results.append({
                "paper_id": p.get("paper_id"),
                "title": p.get("title"),
                "year": p.get("year"),
                "doi": p.get("doi"),
                "authors": p.get("authors")
            })
        results.sort(key=lambda x: x.get("year") or 0, reverse=True)
        return results

    def get_molecule_context(self, molecule_name: str) -> dict:
        papers = self.find_papers_for_molecule(molecule_name)
        reactions = self.find_reactions_for_molecule(molecule_name)

        co_mentioned = []
        papers_with_mol = list(self.db.graph_papers.find({"mentions_molecules": molecule_name}))
        mol_counts = {}
        for p in papers_with_mol:
            for m in p.get("mentions_molecules", []):
                if m != molecule_name:
                    mol_counts[m] = mol_counts.get(m, 0) + 1
                    
        for m, count in sorted(mol_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            co_mentioned.append({"molecule": m, "co_occurrences": count})

        return {
            "molecule": molecule_name,
            "papers": papers,
            "reactions": reactions,
            "co_mentioned_molecules": co_mentioned,
        }

    def get_graph_stats(self) -> dict:
        papers_count = self.db.graph_papers.count_documents({})
        molecules_count = self.db.graph_molecules.count_documents({})
        reactions_count = self.db.graph_reactions.count_documents({})
        
        return {
            "node_counts": {
                "Paper": papers_count,
                "Molecule": molecules_count,
                "Reaction": reactions_count,
            },
            "relationship_counts": {
                "MENTIONS": papers_count * 2,
                "REPORTS": reactions_count,
                "PRODUCES": reactions_count
            },
        }

    def populate_from_paper(self, paper_data: dict, chunks: list[dict]):
        self.add_paper(paper_data)

        for entity in paper_data.get("chemical_entities", []):
            self.add_molecule(entity)
            self.link_paper_molecule(paper_data["paper_id"], entity)

        for chunk in chunks:
            for reaction in chunk.get("reactions", []):
                conditions = {
                    "catalyst": chunk.get("catalyst"),
                    "solvent": chunk.get("solvent"),
                    "temperature": chunk.get("temperature"),
                    "yield_value": chunk.get("yield_value"),
                }
                self.add_reaction(reaction, "extracted", paper_data["paper_id"], conditions)

    def clear_graph(self):
        self.db.graph_papers.delete_many({})
        self.db.graph_molecules.delete_many({})
        self.db.graph_reactions.delete_many({})


knowledge_graph = KnowledgeGraph()
