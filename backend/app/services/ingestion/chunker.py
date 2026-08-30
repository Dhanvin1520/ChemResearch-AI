import re
from typing import Optional
from app.config import settings
from app.services.chemistry.entity_extractor import entity_extractor


class ChemistryAwareChunker:
    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.reaction_boundary_patterns = [
            re.compile(r"(?:Step\s+\d+|Procedure\s+\d+|Compound\s+\d+)", re.IGNORECASE),
            re.compile(r"(?:General\s+procedure|Typical\s+procedure|Representative\s+procedure)", re.IGNORECASE),
            re.compile(r"(?:Synthesis\s+of|Preparation\s+of|Formation\s+of)", re.IGNORECASE),
            re.compile(r"(?:Table\s+\d+|Figure\s+\d+|Scheme\s+\d+)", re.IGNORECASE),
            re.compile(r"(?:Entry\s+\d+|Example\s+\d+|Run\s+\d+)", re.IGNORECASE),
        ]

    def chunk_text(self, text: str, section: str = "unknown") -> list[dict]:
        if not text or not text.strip():
            return []

        paragraphs = self._split_into_paragraphs(text)
        raw_chunks = self._merge_paragraphs_into_chunks(paragraphs)
        enriched_chunks = []

        for idx, chunk_text in enumerate(raw_chunks):
            entities = entity_extractor.extract_experimental_conditions(chunk_text)
            molecules = entity_extractor.extract_molecules(chunk_text)

            chunk = {
                "content": chunk_text,
                "section": section,
                "chunk_index": idx,
                "token_count": self._estimate_tokens(chunk_text),
                "chemical_entities": molecules,
                "catalyst": entities["catalyst"],
                "solvent": entities["solvent"],
                "temperature": entities["temperature"],
                "yield_value": entities["yield_value"],
                "conditions": {
                    "reaction_time": entities["reaction_time"],
                    "pressure": entities["pressure"],
                    "all_catalysts": entities["all_catalysts"],
                    "all_solvents": entities["all_solvents"],
                    "all_temperatures": entities["all_temperatures"],
                    "all_yields": entities["all_yields"],
                },
                "reactions": [],
            }

            from app.services.chemistry.reaction_service import reaction_service
            classified = reaction_service.classify_reaction(chunk_text)
            if classified:
                chunk["reactions"] = [r["reaction_name"] for r in classified[:3]]

            enriched_chunks.append(chunk)

        return enriched_chunks

    def chunk_sections(self, sections: dict[str, str]) -> list[dict]:
        all_chunks = []
        for section_name, section_text in sections.items():
            if section_name.lower() in ("references", "bibliography", "acknowledgements", "acknowledgments", "author information"):
                continue
            chunks = self.chunk_text(section_text, section=section_name)
            all_chunks.extend(chunks)
        return all_chunks

    def _split_into_paragraphs(self, text: str) -> list[str]:
        paragraphs = re.split(r"\n\s*\n", text)
        result = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if self._estimate_tokens(para) > self.chunk_size * 1.5:
                sub_parts = self._split_long_paragraph(para)
                result.extend(sub_parts)
            else:
                result.append(para)

        return result

    def _split_long_paragraph(self, text: str) -> list[str]:
        for pattern in self.reaction_boundary_patterns:
            parts = pattern.split(text)
            if len(parts) > 1:
                matches = pattern.findall(text)
                result = []
                for i, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        if i > 0 and i - 1 < len(matches):
                            part = matches[i - 1] + " " + part
                        result.append(part)
                if len(result) > 1:
                    return result

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            if current_tokens + sentence_tokens > self.chunk_size and current:
                chunks.append(" ".join(current))
                overlap_sentences = current[-2:] if len(current) >= 2 else current[-1:]
                current = list(overlap_sentences)
                current_tokens = sum(self._estimate_tokens(s) for s in current)

            current.append(sentence)
            current_tokens += sentence_tokens

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _merge_paragraphs_into_chunks(self, paragraphs: list[str]) -> list[str]:
        chunks = []
        current_parts = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)

            if para_tokens > self.chunk_size:
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_tokens = 0
                chunks.append(para)
                continue

            if current_tokens + para_tokens > self.chunk_size and current_parts:
                chunks.append("\n\n".join(current_parts))
                overlap_parts = current_parts[-1:] if current_parts else []
                current_parts = list(overlap_parts)
                current_tokens = sum(self._estimate_tokens(p) for p in current_parts)

            current_parts.append(para)
            current_tokens += para_tokens

        if current_parts:
            chunks.append("\n\n".join(current_parts))

        return chunks

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split()) * 4 // 3


chunker = ChemistryAwareChunker()
