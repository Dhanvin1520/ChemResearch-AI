import re
from typing import Optional
from app.config import settings


VERIFICATION_PROMPT = """You are a citation verification expert. For each claim in the answer below, determine if it is supported by the provided evidence.

Answer to verify:
{answer}

Evidence sources:
{evidence_text}

For each claim, respond with a JSON array where each element has:
- "claim": the specific claim text
- "supported": true/false
- "supporting_citation": the citation number [N] if supported, null if not
- "confidence": 0.0-1.0 confidence that the citation supports the claim

Respond ONLY with valid JSON array."""


class CitationVerifier:
    def __init__(self):
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

    def verify(self, answer: str, evidence: list[dict], citations: list[dict]) -> dict:
        if settings.openai_api_key:
            return self._verify_with_llm(answer, evidence, citations)
        return self._verify_with_heuristics(answer, evidence, citations)

    def _verify_with_llm(self, answer: str, evidence: list[dict], citations: list[dict]) -> dict:
        import json
        llm = self._get_llm_client()
        if not llm:
            return self._verify_with_heuristics(answer, evidence, citations)

        evidence_text = ""
        for i, ev in enumerate(evidence, 1):
            evidence_text += f"[{i}] {ev.get('content', '')[:400]}\n\n"

        prompt = VERIFICATION_PROMPT.format(answer=answer, evidence_text=evidence_text)
        response = llm.invoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]

        try:
            verification_results = json.loads(content)
        except json.JSONDecodeError:
            return self._verify_with_heuristics(answer, evidence, citations)

        total_claims = len(verification_results)
        supported_claims = sum(1 for v in verification_results if v.get("supported", False))

        citation_score = supported_claims / total_claims if total_claims > 0 else 0.0

        verified_answer = answer
        for v in verification_results:
            if not v.get("supported", False) and v.get("confidence", 0) < 0.3:
                claim = v.get("claim", "")
                if claim and len(claim) > 20:
                    verified_answer = verified_answer.replace(
                        claim,
                        f"[UNVERIFIED] {claim}"
                    )

        return {
            "verified_answer": verified_answer,
            "citation_score": round(citation_score, 4),
            "total_claims": total_claims,
            "supported_claims": supported_claims,
            "verification_details": verification_results,
        }

    def _verify_with_heuristics(self, answer: str, evidence: list[dict], citations: list[dict]) -> dict:
        sentences = re.split(r"(?<=[.!?])\s+", answer)
        total_claims = 0
        supported_claims = 0
        verification_details = []

        citation_pattern = re.compile(r"\[(\d+)\]")

        evidence_contents = {}
        for i, ev in enumerate(evidence, 1):
            evidence_contents[i] = ev.get("content", "").lower()

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 15:
                continue

            is_factual = self._is_factual_claim(sentence)
            if not is_factual:
                continue

            total_claims += 1
            cited_refs = citation_pattern.findall(sentence)

            is_supported = False
            supporting_citation = None

            if cited_refs:
                for ref in cited_refs:
                    ref_idx = int(ref)
                    if ref_idx in evidence_contents:
                        key_terms = self._extract_key_terms(sentence)
                        evidence_text = evidence_contents[ref_idx]
                        matching_terms = sum(1 for t in key_terms if t.lower() in evidence_text)
                        if matching_terms >= max(1, len(key_terms) // 3):
                            is_supported = True
                            supporting_citation = ref_idx
                            break

            if is_supported:
                supported_claims += 1

            verification_details.append({
                "claim": sentence[:200],
                "supported": is_supported,
                "supporting_citation": supporting_citation,
                "confidence": 0.8 if is_supported else 0.2,
            })

        citation_score = supported_claims / total_claims if total_claims > 0 else 1.0

        return {
            "verified_answer": answer,
            "citation_score": round(citation_score, 4),
            "total_claims": total_claims,
            "supported_claims": supported_claims,
            "verification_details": verification_details,
        }

    def _is_factual_claim(self, sentence: str) -> bool:
        non_factual_starts = [
            "based on", "in summary", "overall", "in conclusion",
            "the following", "here are", "note that", "it should be noted",
            "**", "---", "key findings", "reported experimental",
        ]
        s_lower = sentence.lower().strip()
        for start in non_factual_starts:
            if s_lower.startswith(start):
                return False

        if "?" in sentence:
            return False

        factual_indicators = [
            r"\d+\s*%", r"\d+\s*°C", r"\d+\s*K\b", "catalyst", "solvent",
            "yield", "temperature", "reported", "found", "showed",
            "demonstrated", "achieved", "obtained", "produced",
            "coupling", "reaction", "synthesis",
        ]
        return any(re.search(pattern, sentence, re.IGNORECASE) for pattern in factual_indicators)

    def _extract_key_terms(self, sentence: str) -> list[str]:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", sentence)
        stop_words = {
            "this", "that", "these", "those", "with", "from", "were",
            "been", "have", "also", "which", "their", "about", "would",
            "could", "should", "into", "than", "more", "other", "some",
        }
        return [w for w in words if w.lower() not in stop_words][:10]


citation_verifier = CitationVerifier()
