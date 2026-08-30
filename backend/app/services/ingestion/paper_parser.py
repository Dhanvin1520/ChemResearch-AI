import re
from typing import Optional


class PaperParser:
    def extract_metadata(self, text: str, filename: Optional[str] = None) -> dict:
        metadata = {
            "title": self._extract_title(text, filename),
            "authors": self._extract_authors(text),
            "year": self._extract_year(text),
            "doi": self._extract_doi(text),
            "journal": self._extract_journal(text),
            "abstract": self._extract_abstract(text),
            "keywords": self._extract_keywords(text),
        }
        return metadata

    def _extract_title(self, text: str, filename: Optional[str] = None) -> str:
        lines = text.strip().split("\n")
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 20 and len(line) < 300:
                if not re.match(r"^\d", line) and not line.lower().startswith(("doi", "http", "www", "volume", "issue", "page")):
                    return line

        if filename:
            name = re.sub(r"\.[^.]+$", "", filename)
            name = re.sub(r"[-_]", " ", name)
            return name.title()

        return "Untitled Paper"

    def _extract_authors(self, text: str) -> list[str]:
        author_section = re.search(
            r"(?:(?:authors?|by)[:\s]*)((?:[A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+(?:\s*,\s*|\s+and\s+|\s*;\s*)){1,20})",
            text[:3000],
            re.IGNORECASE,
        )
        if author_section:
            authors_text = author_section.group(1)
            authors = re.split(r"\s*[,;]\s*|\s+and\s+", authors_text)
            return [a.strip() for a in authors if a.strip() and len(a.strip()) > 2]

        name_pattern = re.compile(r"([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)")
        lines = text.split("\n")
        for line in lines[1:8]:
            names = name_pattern.findall(line)
            if len(names) >= 2:
                return names[:10]

        return []

    def _extract_year(self, text: str) -> Optional[int]:
        year_patterns = [
            re.compile(r"(?:published|received|accepted|©|copyright)\s*:?\s*(\d{4})", re.IGNORECASE),
            re.compile(r"\b(20[0-2]\d)\b"),
            re.compile(r"\b(19[89]\d)\b"),
        ]

        for pattern in year_patterns:
            match = pattern.search(text[:5000])
            if match:
                year = int(match.group(1))
                if 1950 <= year <= 2030:
                    return year

        return None

    def _extract_doi(self, text: str) -> Optional[str]:
        doi_pattern = re.compile(r"(?:doi[:\s]*)?(?:https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/[^\s,;\"'>\]]+)", re.IGNORECASE)
        match = doi_pattern.search(text[:5000])
        if match:
            doi = match.group(1).rstrip(".")
            return doi
        return None

    def _extract_journal(self, text: str) -> Optional[str]:
        journal_patterns = [
            re.compile(r"(?:journal|published\s+in)[:\s]*([A-Za-z\s&]+?)(?:\s*,|\s*\d|\s*\n)", re.IGNORECASE),
            re.compile(r"((?:Journal|Angewandte|Chemical|Organic|Inorganic|Nature|Science|ACS|JACS|Chem\.?\s*(?:Rev|Commun|Soc|Eur))[A-Za-z\s\.&]*)", re.IGNORECASE),
        ]

        for pattern in journal_patterns:
            match = pattern.search(text[:3000])
            if match:
                journal = match.group(1).strip()
                if len(journal) > 3:
                    return journal

        return None

    def _extract_abstract(self, text: str) -> Optional[str]:
        abstract_pattern = re.compile(
            r"(?:abstract)[:\s]*\n?(.*?)(?=\n\s*(?:introduction|keywords|1\.|background)|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        match = abstract_pattern.search(text[:10000])
        if match:
            abstract = match.group(1).strip()
            abstract = re.sub(r"\s+", " ", abstract)
            if len(abstract) > 50:
                return abstract[:3000]

        return None

    def _extract_keywords(self, text: str) -> list[str]:
        keyword_pattern = re.compile(
            r"(?:keywords?|key\s*words?)[:\s]*\n?(.*?)(?=\n\s*(?:\d+\.|introduction|abstract)|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        match = keyword_pattern.search(text[:10000])
        if match:
            keywords_text = match.group(1).strip()
            keywords = re.split(r"\s*[,;·•]\s*|\s*\n\s*", keywords_text)
            return [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1][:15]

        return []

    def extract_references(self, text: str) -> list[dict]:
        ref_section = re.search(
            r"(?:references|bibliography)\s*\n(.*?)(?=\n\s*(?:supplementary|supporting|appendix)|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not ref_section:
            return []

        ref_text = ref_section.group(1)
        ref_pattern = re.compile(r"(?:^\s*\[?\d+\]?\.?\s*)(.*?)(?=\n\s*\[?\d+\]?\.?\s*|\Z)", re.MULTILINE | re.DOTALL)
        references = []

        for match in ref_pattern.finditer(ref_text):
            ref = match.group(1).strip()
            ref = re.sub(r"\s+", " ", ref)
            if len(ref) > 10:
                doi = None
                doi_match = re.search(r"10\.\d{4,9}/[^\s,;\"'>\]]+", ref)
                if doi_match:
                    doi = doi_match.group(0).rstrip(".")

                references.append({
                    "text": ref[:500],
                    "doi": doi,
                })

        return references[:100]


paper_parser = PaperParser()
