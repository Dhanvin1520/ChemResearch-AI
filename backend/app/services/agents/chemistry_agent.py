from typing import Optional
from app.services.chemistry.molecule_service import molecule_service
from app.services.chemistry.reaction_service import reaction_service


class ChemistryAgent:
    def __init__(self):
        self.molecule_service = molecule_service
        self.reaction_service = reaction_service

    def process(self, query_plan: dict) -> dict:
        result = {
            "molecules": {},
            "reactions": {},
            "conversions": [],
        }

        for mol_name in query_plan.get("target_molecules", []):
            mol_info = self._analyze_molecule(mol_name)
            if mol_info:
                result["molecules"][mol_name] = mol_info

        for reaction_name in query_plan.get("target_reactions", []):
            rxn_info = self._analyze_reaction(reaction_name)
            if rxn_info:
                result["reactions"][reaction_name] = rxn_info

        return result

    def _analyze_molecule(self, name: str) -> Optional[dict]:
        smiles = self.molecule_service.name_to_smiles(name)
        if not smiles:
            if self.molecule_service.validate_smiles(name):
                smiles = name
            else:
                return None

        analysis = self.molecule_service.get_full_analysis(smiles, name=name)
        return analysis

    def _analyze_reaction(self, reaction_name: str) -> Optional[dict]:
        info = self.reaction_service.get_reaction_info(reaction_name)
        return info

    def convert_molecule(self, input_value: str, input_type: str = "name") -> Optional[dict]:
        if input_type == "name":
            smiles = self.molecule_service.name_to_smiles(input_value)
            if not smiles:
                return None
            analysis = self.molecule_service.get_full_analysis(smiles, name=input_value)
            return analysis

        elif input_type == "smiles":
            if not self.molecule_service.validate_smiles(input_value):
                return None
            analysis = self.molecule_service.get_full_analysis(input_value)
            return analysis

        return None

    def compare_molecules(self, smiles1: str, smiles2: str) -> Optional[dict]:
        similarity = self.molecule_service.calculate_similarity(smiles1, smiles2)
        if not similarity:
            return None

        props1 = self.molecule_service.get_molecular_properties(smiles1)
        props2 = self.molecule_service.get_molecular_properties(smiles2)

        return {
            "similarity": similarity,
            "molecule_1": props1,
            "molecule_2": props2,
        }

    def classify_reaction_from_text(self, text: str) -> list[dict]:
        return self.reaction_service.classify_reaction(text)


chemistry_agent = ChemistryAgent()
