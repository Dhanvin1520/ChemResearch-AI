import re
from pathlib import Path
from typing import Optional
import pdfplumber


SECTION_HEADERS = [
    "abstract",
    "introduction",
    "background",
    "literature review",
    "theory",
    "methods",
    "methodology",
    "materials and methods",
    "experimental",
    "experimental section",
    "experimental procedures",
    "general procedure",
    "synthesis",
    "synthetic procedures",
    "results",
    "results and discussion",
    "discussion",
    "analysis",
    "characterization",
    "spectroscopic data",
    "computational details",
    "supporting information",
    "supplementary",
    "conclusion",
    "conclusions",
    "summary",
    "acknowledgements",
    "acknowledgments",
    "references",
    "bibliography",
    "notes",
    "author information",
    "funding",
    "conflicts of interest",
    "declaration",
]

SECTION_PATTERN = re.compile(
    r"^\s*(?:\d+[\.\)]\s*)?(" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class PDFProcessor:
    def __init__(self):
        self.section_pattern = SECTION_PATTERN

    def extract_text(self, filepath: str) -> Optional[str]:
        path = Path(filepath)
        if not path.exists():
            return None
        if path.suffix.lower() != ".pdf":
            return None

        full_text = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text = self._clean_text(text)
                    full_text.append(text)

        return "\n\n".join(full_text)

    def extract_sections(self, filepath: str) -> dict[str, str]:
        full_text = self.extract_text(filepath)
        if not full_text:
            return {}

        return self.parse_sections(full_text)

    def parse_sections(self, text: str) -> dict[str, str]:
        sections = {}
        current_section = "preamble"
        current_content = []

        for line in text.split("\n"):
            match = self.section_pattern.match(line.strip())
            if match:
                if current_content:
                    content = "\n".join(current_content).strip()
                    if content:
                        sections[current_section] = content
                current_section = match.group(1).lower().strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            content = "\n".join(current_content).strip()
            if content:
                sections[current_section] = content

        return sections

    def extract_tables(self, filepath: str) -> list[dict]:
        path = Path(filepath)
        if not path.exists():
            return []

        tables = []
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                for table_idx, table in enumerate(page_tables):
                    if table and len(table) > 1:
                        headers = [str(cell).strip() if cell else "" for cell in table[0]]
                        rows = []
                        for row in table[1:]:
                            rows.append([str(cell).strip() if cell else "" for cell in row])

                        tables.append({
                            "page": page_num,
                            "table_index": table_idx,
                            "headers": headers,
                            "rows": rows,
                            "text": self._table_to_text(headers, rows),
                        })

        return tables

    def _table_to_text(self, headers: list[str], rows: list[list[str]]) -> str:
        lines = []
        lines.append(" | ".join(headers))
        lines.append("-" * len(lines[0]))
        for row in rows:
            lines.append(" | ".join(row))
        return "\n".join(lines)

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    def get_page_count(self, filepath: str) -> int:
        path = Path(filepath)
        if not path.exists():
            return 0

        with pdfplumber.open(filepath) as pdf:
            return len(pdf.pages)


pdf_processor = PDFProcessor()
