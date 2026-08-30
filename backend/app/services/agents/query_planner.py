import json
from typing import Optional
from app.config import settings


QUERY_PLANNER_PROMPT = """You are a chemistry research query planner. Analyze the user's research question and create a structured query plan.

Given the question, determine:
1. query_type: One of "synthesis", "property", "reaction", "comparison", "mechanism", "conditions", "review", "general"
2. target_molecules: List of specific molecules, compounds, or materials mentioned
3. target_reactions: List of specific reaction types mentioned (e.g., Suzuki coupling, Grignard)
4. conditions_of_interest: What experimental conditions the user cares about (catalyst, solvent, temperature, yield, etc.)
5. time_range: Any year or date range constraints (as {"from": YYYY, "to": YYYY})
6. search_keywords: Key terms to search for in literature
7. requires_chemistry_tools: Whether RDKit tools are needed (true/false)
8. requires_literature_search: Whether literature search is needed (true/false)

Respond ONLY with valid JSON matching this schema, no markdown or explanation.

User question: {question}"""


class QueryPlanner:
    def __init__(self):
        self.llm_client = None

    def _get_llm_client(self):
        if self.llm_client is None:
            from langchain_openai import ChatOpenAI
            self.llm_client = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0,
            )
        return self.llm_client

    def plan(self, question: str) -> dict:
        if settings.openai_api_key:
            return self._plan_with_llm(question)
        return self._plan_with_heuristics(question)

    def _plan_with_llm(self, question: str) -> dict:
        llm = self._get_llm_client()
        prompt = QUERY_PLANNER_PROMPT.format(question=question)
        response = llm.invoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]

        plan = json.loads(content)
        return self._validate_plan(plan)

    def _plan_with_heuristics(self, question: str) -> dict:
        q_lower = question.lower()

        query_type = "general"
        if any(w in q_lower for w in ["synthesize", "synthesis", "prepare", "make", "route"]):
            query_type = "synthesis"
        elif any(w in q_lower for w in ["property", "properties", "molecular weight", "boiling point", "melting point", "logp"]):
            query_type = "property"
        elif any(w in q_lower for w in ["reaction", "coupling", "addition", "substitution", "elimination", "oxidation", "reduction"]):
            query_type = "reaction"
        elif any(w in q_lower for w in ["compare", "comparison", "versus", "vs", "difference"]):
            query_type = "comparison"
        elif any(w in q_lower for w in ["mechanism", "pathway", "step", "intermediate"]):
            query_type = "mechanism"
        elif any(w in q_lower for w in ["catalyst", "solvent", "temperature", "conditions", "yield"]):
            query_type = "conditions"
        elif any(w in q_lower for w in ["review", "overview", "survey", "summary"]):
            query_type = "review"

        from app.services.chemistry.molecule_service import molecule_service
        from app.services.chemistry.reaction_service import reaction_service
        from app.services.chemistry.entity_extractor import entity_extractor

        target_molecules = entity_extractor.extract_molecules(question)
        smiles_molecules = []
        for mol_name in target_molecules:
            smiles = molecule_service.name_to_smiles(mol_name)
            if smiles:
                smiles_molecules.append(mol_name)

        classified_reactions = reaction_service.classify_reaction(question)
        target_reactions = [r["reaction_name"] for r in classified_reactions]

        conditions = entity_extractor.extract_experimental_conditions(question)
        conditions_of_interest = []
        if conditions["catalyst"]:
            conditions_of_interest.append("catalyst")
        if conditions["solvent"]:
            conditions_of_interest.append("solvent")
        if conditions["temperature"]:
            conditions_of_interest.append("temperature")
        if any(w in q_lower for w in ["yield", "conversion", "selectivity"]):
            conditions_of_interest.append("yield")

        if not conditions_of_interest and query_type in ("synthesis", "conditions", "reaction"):
            conditions_of_interest = ["catalyst", "solvent", "temperature", "yield"]

        import re
        time_range = None
        year_match = re.findall(r"\b(19[89]\d|20[0-2]\d)\b", question)
        if len(year_match) >= 2:
            years = sorted([int(y) for y in year_match])
            time_range = {"from": years[0], "to": years[-1]}
        elif len(year_match) == 1:
            year = int(year_match[0])
            if "after" in q_lower or "since" in q_lower:
                time_range = {"from": year, "to": 2026}
            elif "before" in q_lower:
                time_range = {"from": 1950, "to": year}

        words = re.findall(r"\b[a-zA-Z]{3,}\b", question)
        stop_words = {
            "the", "and", "for", "are", "was", "were", "been", "being",
            "have", "has", "had", "what", "which", "that", "this", "with",
            "from", "about", "between", "how", "does", "can", "could",
            "would", "should", "will", "used", "using", "reported",
        }
        search_keywords = [w for w in words if w.lower() not in stop_words]
        search_keywords.extend(target_reactions)

        requires_chemistry = bool(smiles_molecules) or query_type == "property" or any(
            w in q_lower for w in ["smiles", "structure", "formula", "molecular", "convert", "rdkit"]
        )

        return self._validate_plan({
            "query_type": query_type,
            "target_molecules": target_molecules,
            "target_reactions": target_reactions,
            "conditions_of_interest": conditions_of_interest,
            "time_range": time_range,
            "search_keywords": search_keywords[:15],
            "requires_chemistry_tools": requires_chemistry,
            "requires_literature_search": True,
        })

    def _validate_plan(self, plan: dict) -> dict:
        defaults = {
            "query_type": "general",
            "target_molecules": [],
            "target_reactions": [],
            "conditions_of_interest": [],
            "time_range": None,
            "search_keywords": [],
            "requires_chemistry_tools": False,
            "requires_literature_search": True,
        }

        for key, default in defaults.items():
            if key not in plan:
                plan[key] = default

        valid_types = ["synthesis", "property", "reaction", "comparison", "mechanism", "conditions", "review", "general"]
        if plan["query_type"] not in valid_types:
            plan["query_type"] = "general"

        return plan


query_planner = QueryPlanner()
