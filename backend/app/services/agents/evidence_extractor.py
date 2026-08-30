from app.services.chemistry.entity_extractor import entity_extractor
from app.config import settings


EXTRACTION_PROMPT = """You are a chemistry information extraction expert. Given a passage from a chemistry paper, extract all experimental conditions and chemical information.

Extract the following fields (use null if not found):
- catalyst: The catalyst used
- solvent: The solvent used
- temperature: Reaction temperature
- yield_value: Reported yield percentage
- reaction_time: Duration of the reaction
- pressure: Reaction pressure
- reaction_type: Type of reaction performed
- substrate: Starting material
- product: Product formed
- base: Base used (if any)
- ligand: Ligand used (if any)
- additives: Any additives used

Respond ONLY with valid JSON. No markdown or explanation.

Passage: {passage}"""


class EvidenceExtractor:
    def __init__(self):
        self.entity_extractor = entity_extractor
        self.llm_client = None

    def _get_llm_client(self):
        if self.llm_client is None and settings.openai_api_key:
            from langchain_openai import ChatOpenAI
            self.llm_client = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0,
            )
        return self.llm_client

    def extract(self, retrieved_chunks: list[dict], query_plan: dict) -> list[dict]:
        evidence_list = []

        for chunk in retrieved_chunks:
            content = chunk.get("content", "")
            regex_extraction = self.entity_extractor.extract_experimental_conditions(content)
            all_entities = self.entity_extractor.extract_all(content)

            evidence = {
                "chunk_id": chunk.get("chunk_id"),
                "paper_id": chunk.get("paper_id"),
                "paper_title": chunk.get("paper_title", ""),
                "section": chunk.get("section", ""),
                "content": content,
                "catalyst": chunk.get("catalyst") or regex_extraction.get("catalyst"),
                "solvent": chunk.get("solvent") or regex_extraction.get("solvent"),
                "temperature": chunk.get("temperature") or regex_extraction.get("temperature"),
                "yield_value": chunk.get("yield_value") or regex_extraction.get("yield_value"),
                "reaction_time": regex_extraction.get("reaction_time"),
                "pressure": regex_extraction.get("pressure"),
                "chemical_entities": chunk.get("chemical_entities", []) or all_entities.get("molecules", []),
                "reactions": chunk.get("reactions", []),
                "relevance_score": chunk.get("rerank_score", chunk.get("retrieval_score", 0)),
                "all_catalysts": regex_extraction.get("all_catalysts", []),
                "all_solvents": regex_extraction.get("all_solvents", []),
                "all_temperatures": regex_extraction.get("all_temperatures", []),
                "all_yields": regex_extraction.get("all_yields", []),
            }

            evidence_list.append(evidence)

        evidence_list = self._deduplicate(evidence_list)
        evidence_list = self._score_by_relevance(evidence_list, query_plan)

        return evidence_list

    def extract_with_llm(self, passage: str) -> dict:
        import json
        llm = self._get_llm_client()
        if not llm:
            return self.entity_extractor.extract_experimental_conditions(passage)

        prompt = EXTRACTION_PROMPT.format(passage=passage)
        response = llm.invoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]

        return json.loads(content)

    def _deduplicate(self, evidence_list: list[dict]) -> list[dict]:
        seen_content = set()
        unique = []

        for evidence in evidence_list:
            content_hash = hash(evidence["content"][:200])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique.append(evidence)

        return unique

    def _score_by_relevance(self, evidence_list: list[dict], query_plan: dict) -> list[dict]:
        conditions_of_interest = set(query_plan.get("conditions_of_interest", []))

        for evidence in evidence_list:
            bonus = 0
            if "catalyst" in conditions_of_interest and evidence.get("catalyst"):
                bonus += 0.1
            if "solvent" in conditions_of_interest and evidence.get("solvent"):
                bonus += 0.1
            if "temperature" in conditions_of_interest and evidence.get("temperature"):
                bonus += 0.1
            if "yield" in conditions_of_interest and evidence.get("yield_value"):
                bonus += 0.1

            target_molecules = set(m.lower() for m in query_plan.get("target_molecules", []))
            found_molecules = set(e.lower() for e in evidence.get("chemical_entities", []))
            if target_molecules & found_molecules:
                bonus += 0.15

            evidence["relevance_score"] = evidence.get("relevance_score", 0) + bonus

        evidence_list.sort(key=lambda x: x["relevance_score"], reverse=True)
        return evidence_list


evidence_extractor = EvidenceExtractor()
