import json
from typing import Optional
from app.config import settings


REASONING_PROMPT = """You are a chemistry research assistant. Based on the evidence extracted from scientific papers, provide a comprehensive, well-structured answer to the research question.

CRITICAL RULES:
1. Every factual claim MUST be supported by a citation in the format [N] where N corresponds to the evidence source number.
2. Include specific experimental data (catalyst, solvent, temperature, yield) when available.
3. Structure your answer with clear sections when appropriate.
4. If evidence is conflicting, acknowledge the discrepancy.
5. Do NOT fabricate information not present in the evidence.
6. When multiple conditions are reported, present them in a comparison table format.

Research Question: {question}

Query Plan: {query_plan}

Evidence Sources:
{evidence_text}

{chemistry_context}

Provide a thorough, citation-grounded answer:"""


class ReasoningAgent:
    def __init__(self):
        self.llm_client = None

    def _get_llm_client(self):
        if self.llm_client is None:
            if settings.openai_api_key:
                from langchain_openai import ChatOpenAI
                self.llm_client = ChatOpenAI(
                    model=settings.openai_model,
                    api_key=settings.openai_api_key,
                    temperature=0.1,
                    max_tokens=3000,
                )
        return self.llm_client

    def reason(
        self,
        question: str,
        evidence: list[dict],
        query_plan: dict,
        chemistry_info: Optional[dict] = None,
    ) -> dict:
        llm = self._get_llm_client()
        if llm:
            return self._reason_with_llm(question, evidence, query_plan, chemistry_info, llm)
        return self._reason_with_template(question, evidence, query_plan, chemistry_info)

    def _reason_with_llm(
        self,
        question: str,
        evidence: list[dict],
        query_plan: dict,
        chemistry_info: Optional[dict],
        llm,
    ) -> dict:
        evidence_text = self._format_evidence(evidence)
        chemistry_context = self._format_chemistry_info(chemistry_info) if chemistry_info else ""

        prompt = REASONING_PROMPT.format(
            question=question,
            query_plan=json.dumps(query_plan, indent=2),
            evidence_text=evidence_text,
            chemistry_context=chemistry_context,
        )

        response = llm.invoke(prompt)
        answer = response.content.strip()

        citations = self._extract_citation_references(answer, evidence)

        return {
            "answer": answer,
            "citations": citations,
            "evidence_used": len(evidence),
        }

    def _reason_with_template(
        self,
        question: str,
        evidence: list[dict],
        query_plan: dict,
        chemistry_info: Optional[dict],
    ) -> dict:
        if not evidence:
            return {
                "answer": "No relevant evidence was found in the literature database for this query. Please try rephrasing your question or ingesting more papers.",
                "citations": [],
                "evidence_used": 0,
            }

        sections = []
        sections.append(f"Based on the analysis of {len(evidence)} relevant passages from the literature:\n")

        conditions_data = []
        for i, ev in enumerate(evidence, 1):
            entry = {"source": i, "paper": ev.get("paper_title", "Unknown")}
            if ev.get("catalyst"):
                entry["catalyst"] = ev["catalyst"]
            if ev.get("solvent"):
                entry["solvent"] = ev["solvent"]
            if ev.get("temperature"):
                entry["temperature"] = ev["temperature"]
            if ev.get("yield_value"):
                entry["yield"] = ev["yield_value"]
            if ev.get("reactions"):
                entry["reaction"] = ", ".join(ev["reactions"])
            conditions_data.append(entry)

        has_conditions = any(
            any(k in entry for k in ["catalyst", "solvent", "temperature", "yield"])
            for entry in conditions_data
        )

        if has_conditions:
            sections.append("**Reported Experimental Conditions:**\n")
            for entry in conditions_data:
                line_parts = [f"[{entry['source']}] {entry['paper']}:"]
                if entry.get("catalyst"):
                    line_parts.append(f"Catalyst: {entry['catalyst']}")
                if entry.get("solvent"):
                    line_parts.append(f"Solvent: {entry['solvent']}")
                if entry.get("temperature"):
                    line_parts.append(f"Temperature: {entry['temperature']}")
                if entry.get("yield"):
                    line_parts.append(f"Yield: {entry['yield']}")
                if entry.get("reaction"):
                    line_parts.append(f"Reaction: {entry['reaction']}")
                sections.append("  " + " | ".join(line_parts))
            sections.append("")

        sections.append("**Key Findings:**\n")
        for i, ev in enumerate(evidence[:5], 1):
            content = ev.get("content", "")
            snippet = content[:300].strip()
            if len(content) > 300:
                snippet += "..."
            sections.append(f"[{i}] From \"{ev.get('paper_title', 'Unknown')}\" ({ev.get('section', 'N/A')} section):")
            sections.append(f"  {snippet}\n")

        if chemistry_info:
            chem_section = self._format_chemistry_summary(chemistry_info)
            if chem_section:
                sections.append(chem_section)

        answer = "\n".join(sections)
        citations = self._build_citations(evidence)

        return {
            "answer": answer,
            "citations": citations,
            "evidence_used": len(evidence),
        }

    def _format_evidence(self, evidence: list[dict]) -> str:
        parts = []
        for i, ev in enumerate(evidence, 1):
            part = f"[{i}] Paper: \"{ev.get('paper_title', 'Unknown')}\"\n"
            part += f"    Section: {ev.get('section', 'N/A')}\n"
            part += f"    Content: {ev.get('content', '')[:500]}\n"

            if ev.get("catalyst"):
                part += f"    Catalyst: {ev['catalyst']}\n"
            if ev.get("solvent"):
                part += f"    Solvent: {ev['solvent']}\n"
            if ev.get("temperature"):
                part += f"    Temperature: {ev['temperature']}\n"
            if ev.get("yield_value"):
                part += f"    Yield: {ev['yield_value']}\n"
            if ev.get("reactions"):
                part += f"    Reactions: {', '.join(ev['reactions'])}\n"

            parts.append(part)

        return "\n".join(parts)

    def _format_chemistry_info(self, chemistry_info: dict) -> str:
        parts = ["Chemistry Analysis:"]

        for name, info in chemistry_info.get("molecules", {}).items():
            if info:
                parts.append(f"\nMolecule: {name}")
                parts.append(f"  SMILES: {info.get('smiles', 'N/A')}")
                parts.append(f"  Formula: {info.get('molecular_formula', 'N/A')}")
                parts.append(f"  MW: {info.get('molecular_weight', 'N/A')}")
                if info.get("functional_groups"):
                    parts.append(f"  Functional groups: {', '.join(info['functional_groups'][:5])}")

        for name, info in chemistry_info.get("reactions", {}).items():
            if info:
                parts.append(f"\nReaction: {info.get('name', name)}")
                parts.append(f"  Type: {info.get('reaction_type', 'N/A')}")
                parts.append(f"  Description: {info.get('description', 'N/A')}")

        return "\n".join(parts)

    def _format_chemistry_summary(self, chemistry_info: dict) -> str:
        parts = ["**Molecular Information:**\n"]
        has_content = False

        for name, info in chemistry_info.get("molecules", {}).items():
            if info:
                has_content = True
                parts.append(f"  {name}: {info.get('molecular_formula', '')} (MW: {info.get('molecular_weight', 'N/A')})")
                if info.get("functional_groups"):
                    parts.append(f"    Functional groups: {', '.join(info['functional_groups'][:5])}")

        return "\n".join(parts) if has_content else ""

    def _extract_citation_references(self, answer: str, evidence: list[dict]) -> list[dict]:
        import re
        citations = []
        cited_indices = set()
        for match in re.finditer(r"\[(\d+)\]", answer):
            idx = int(match.group(1))
            cited_indices.add(idx)

        for idx in sorted(cited_indices):
            if 1 <= idx <= len(evidence):
                ev = evidence[idx - 1]
                citations.append({
                    "citation_id": idx,
                    "paper_title": ev.get("paper_title", "Unknown"),
                    "paper_id": ev.get("paper_id"),
                    "section": ev.get("section", ""),
                    "evidence_text": ev.get("content", "")[:500],
                    "doi": ev.get("paper_doi"),
                    "year": ev.get("paper_year"),
                    "relevance_score": ev.get("relevance_score", 0),
                })

        return citations

    def _build_citations(self, evidence: list[dict]) -> list[dict]:
        citations = []
        for i, ev in enumerate(evidence, 1):
            citations.append({
                "citation_id": i,
                "paper_title": ev.get("paper_title", "Unknown"),
                "paper_id": ev.get("paper_id"),
                "section": ev.get("section", ""),
                "evidence_text": ev.get("content", "")[:500],
                "doi": ev.get("paper_doi"),
                "year": ev.get("paper_year"),
                "relevance_score": ev.get("relevance_score", 0),
            })
        return citations


reasoning_agent = ReasoningAgent()
