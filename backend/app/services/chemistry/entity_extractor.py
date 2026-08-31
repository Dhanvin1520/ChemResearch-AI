import re
from typing import Optional


SOLVENT_DICTIONARY = {
    "dmf": "N,N-Dimethylformamide",
    "n,n-dimethylformamide": "N,N-Dimethylformamide",
    "thf": "Tetrahydrofuran",
    "tetrahydrofuran": "Tetrahydrofuran",
    "dmso": "Dimethyl sulfoxide",
    "dimethyl sulfoxide": "Dimethyl sulfoxide",
    "dcm": "Dichloromethane",
    "ch2cl2": "Dichloromethane",
    "dichloromethane": "Dichloromethane",
    "meoh": "Methanol",
    "methanol": "Methanol",
    "etoh": "Ethanol",
    "ethanol": "Ethanol",
    "acetonitrile": "Acetonitrile",
    "mecn": "Acetonitrile",
    "ch3cn": "Acetonitrile",
    "toluene": "Toluene",
    "benzene": "Benzene",
    "dioxane": "1,4-Dioxane",
    "1,4-dioxane": "1,4-Dioxane",
    "et2o": "Diethyl ether",
    "diethyl ether": "Diethyl ether",
    "hexane": "Hexane",
    "hexanes": "Hexane",
    "pentane": "Pentane",
    "chloroform": "Chloroform",
    "chcl3": "Chloroform",
    "water": "Water",
    "h2o": "Water",
    "dce": "1,2-Dichloroethane",
    "1,2-dichloroethane": "1,2-Dichloroethane",
    "dme": "1,2-Dimethoxyethane",
    "nmp": "N-Methyl-2-pyrrolidone",
    "dma": "N,N-Dimethylacetamide",
    "dmac": "N,N-Dimethylacetamide",
    "etoac": "Ethyl acetate",
    "ethyl acetate": "Ethyl acetate",
    "acetone": "Acetone",
    "pyridine": "Pyridine",
    "et3n": "Triethylamine",
    "triethylamine": "Triethylamine",
    "dipa": "Diisopropylamine",
    "diisopropylamine": "Diisopropylamine",
    "ipoh": "Isopropanol",
    "isopropanol": "Isopropanol",
    "2-propanol": "Isopropanol",
    "dmpu": "1,3-Dimethyl-3,4,5,6-tetrahydro-2(1H)-pyrimidinone",
    "hmpa": "Hexamethylphosphoramide",
    "acetic acid": "Acetic acid",
    "acooh": "Acetic acid",
    "formamide": "Formamide",
    "nitromethane": "Nitromethane",
    "carbon tetrachloride": "Carbon tetrachloride",
    "ccl4": "Carbon tetrachloride",
    "cs2": "Carbon disulfide",
    "carbon disulfide": "Carbon disulfide",
}


CATALYST_PATTERNS = [
    r"Pd\(PPh3\)4",
    r"Pd\(PPh3\)2Cl2",
    r"Pd\(dppf\)Cl2",
    r"Pd\(OAc\)2",
    r"Pd2\(dba\)3",
    r"PdCl2",
    r"Pd/C",
    r"Pd\(0\)",
    r"Pd\(II\)",
    r"CuI",
    r"CuBr",
    r"CuCl",
    r"Cu\(OAc\)2",
    r"NiCl2",
    r"Ni\(cod\)2",
    r"Ni\(0\)",
    r"RuCl2",
    r"RhCl\(PPh3\)3",
    r"Rh2\(OAc\)4",
    r"Ir\(cod\)",
    r"AlCl3",
    r"BF3[\.\·]OEt2",
    r"TiCl4",
    r"ZnCl2",
    r"SnCl4",
    r"FeCl3",
    r"FeCl2",
    r"MgBr2",
    r"LiAlH4",
    r"NaBH4",
    r"DIBAL-?H",
    r"LDA",
    r"LHMDS",
    r"KHMDS",
    r"NaH",
    r"KOH",
    r"NaOH",
    r"K2CO3",
    r"Cs2CO3",
    r"Na2CO3",
    r"Et3N",
    r"DMAP",
    r"DBU",
    r"DABCO",
    r"p-TsOH",
    r"H2SO4",
    r"HCl",
    r"TFA",
    r"mCPBA",
    r"Grubbs",
    r"Hoveyda-Grubbs",
    r"Schrock",
    r"BINAP",
    r"XPhos",
    r"SPhos",
    r"JohnPhos",
    r"DavePhos",
    r"Pt/C",
    r"PtO2",
    r"Raney\s*Ni",
    r"Wilkinson['\u2019]?s?\s*catalyst",
    r"Crabtree['\u2019]?s?\s*catalyst",
]

TEMPERATURE_PATTERNS = [
    r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)\s*[°ºo]\s*C",
    r"(?<![\d.\-])(-?\d+(?:\.\d+)?)\s*[°ºo]\s*C",
    r"(?<![\d.\-])(-?\d+(?:\.\d+)?)\s*°?\s*[Cc]elsius",
    r"(?<![\d.\-])(-?\d+(?:\.\d+)?)\s*K(?:\b|elvin)",
    r"room\s*temp(?:erature)?",
    r"rt\b",
    r"reflux",
    r"ambient\s*temp(?:erature)?",
    r"heating\s*(?:at|to)\s*(-?\d+)",
    r"cooled?\s*(?:to|at)\s*(-?\d+)",
]

YIELD_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*%\s*(?:yield|isolated|conversion)",
    r"yield[:\s]+(\d+(?:\.\d+)?)\s*%",
    r"(\d+(?:\.\d+)?)\s*%\s*(?:ee|de|dr)",
    r"quantitative\s*yield",
    r"moderate\s*yield",
    r"excellent\s*yield",
    r"good\s*yield",
    r"poor\s*yield",
    r"low\s*yield",
    r"(\d+(?:\.\d+)?)\s*%",
]

TIME_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(?:h(?:ours?)?|hrs?)\b",
    r"(\d+(?:\.\d+)?)\s*min(?:utes?)?\b",
    r"(\d+(?:\.\d+)?)\s*days?\b",
    r"overnight",
    r"(\d+(?:\.\d+)?)\s*seconds?\b",
]

PRESSURE_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(?:atm|atmosphere)",
    r"(\d+(?:\.\d+)?)\s*(?:bar|mbar)",
    r"(\d+(?:\.\d+)?)\s*(?:psi|PSI)",
    r"(\d+(?:\.\d+)?)\s*(?:Pa|kPa|MPa)",
    r"(\d+(?:\.\d+)?)\s*(?:Torr|torr|mmHg)",
    r"vacuum",
    r"under\s*(?:N2|Ar|argon|nitrogen)",
    r"inert\s*atmosphere",
]


class ChemicalEntityExtractor:
    def __init__(self):
        self.solvent_dict = SOLVENT_DICTIONARY
        self.catalyst_patterns = [re.compile(p, re.IGNORECASE) for p in CATALYST_PATTERNS]
        self.temperature_patterns = [re.compile(p, re.IGNORECASE) for p in TEMPERATURE_PATTERNS]
        self.yield_patterns = [re.compile(p, re.IGNORECASE) for p in YIELD_PATTERNS]
        self.time_patterns = [re.compile(p, re.IGNORECASE) for p in TIME_PATTERNS]
        self.pressure_patterns = [re.compile(p, re.IGNORECASE) for p in PRESSURE_PATTERNS]

        self.iupac_pattern = re.compile(
            r"\b(?:\d+[,-])*(?:(?:methyl|ethyl|propyl|butyl|pentyl|hexyl|heptyl|octyl|"
            r"nonyl|decyl|phenyl|benzyl|vinyl|allyl|cyclo|iso|tert|sec|neo|ortho|meta|"
            r"para|amino|hydroxy|oxo|chloro|bromo|fluoro|iodo|nitro|cyano|carboxy|"
            r"mercapto|thio|oxy|di|tri|tetra|penta|hexa|bis|mono)[a-z]*)+(?:ane|ene|"
            r"yne|ol|al|one|oic\s*acid|amine|amide|ester|ether|ate|ide|ine|ose|ite|"
            r"yl|oxy)\b",
            re.IGNORECASE,
        )

        self.common_molecule_pattern = re.compile(
            r"\b(?:aspirin|caffeine|ibuprofen|paracetamol|acetaminophen|penicillin|"
            r"morphine|insulin|glucose|fructose|sucrose|cholesterol|nicotine|dopamine|"
            r"serotonin|adrenaline|epinephrine|norepinephrine|melatonin|testosterone|"
            r"estrogen|progesterone|cortisol|histamine|acetylcholine|glycine|alanine|"
            r"valine|leucine|isoleucine|proline|phenylalanine|tryptophan|methionine|"
            r"serine|threonine|cysteine|tyrosine|asparagine|glutamine|aspartic\s*acid|"
            r"glutamic\s*acid|lysine|arginine|histidine|urea|adenine|guanine|cytosine|"
            r"thymine|uracil|ribose|deoxyribose|cellulose|starch|glycogen|chitin|"
            r"acetic\s*acid|citric\s*acid|lactic\s*acid|oxalic\s*acid|benzoic\s*acid|"
            r"salicylic\s*acid|ascorbic\s*acid|palmitic\s*acid|stearic\s*acid|"
            r"oleic\s*acid|linoleic\s*acid|retinol|tocopherol|niacin|thiamine|"
            r"riboflavin|pyridoxine|biotin|folate|cobalamin)\b",
            re.IGNORECASE,
        )

    def extract_catalysts(self, text: str) -> list[str]:
        found = []
        for pattern in self.catalyst_patterns:
            matches = pattern.findall(text)
            for match in matches:
                catalyst = match.strip() if isinstance(match, str) else pattern.pattern
                if catalyst not in found:
                    found.append(catalyst)

        catalyst_regex = re.compile(
            r"\b(?:catalyst|catalyzed\s+by|in\s+the\s+presence\s+of)\s*[:\s]*([A-Za-z0-9\(\)\[\],/\.\s]{2,50}?)(?:\s*[\.,;]|\s+(?:was|were|in|at|under))",
            re.IGNORECASE,
        )
        for match in catalyst_regex.finditer(text):
            candidate = match.group(1).strip()
            if candidate and candidate not in found and len(candidate) > 1:
                found.append(candidate)

        return found

    def extract_solvents(self, text: str) -> list[str]:
        found = []
        text_lower = text.lower()

        for abbrev, full_name in self.solvent_dict.items():
            pattern = re.compile(r"\b" + re.escape(abbrev) + r"\b", re.IGNORECASE)
            if pattern.search(text):
                if full_name not in found:
                    found.append(full_name)

        solvent_context = re.compile(
            r"(?:dissolved\s+in|solvent[:\s]+|in\s+(?:dry\s+)?|suspended\s+in)\s*([A-Za-z0-9\s/\-,]{2,40}?)(?:\s*[\.,;(]|\s+(?:was|were|at|under|and\s+(?:heated|stirred|refluxed)))",
            re.IGNORECASE,
        )
        for match in solvent_context.finditer(text):
            candidate = match.group(1).strip().lower()
            if candidate in self.solvent_dict:
                full_name = self.solvent_dict[candidate]
                if full_name not in found:
                    found.append(full_name)

        return found

    def extract_temperatures(self, text: str) -> list[str]:
        found = []
        for pattern in self.temperature_patterns:
            for match in pattern.finditer(text):
                temp_str = match.group(0).strip()
                if temp_str.lower() in ("rt", "room temperature", "room temp", "ambient temperature"):
                    temp_str = "Room temperature (~25°C)"
                elif temp_str.lower() == "reflux":
                    temp_str = "Reflux"
                if temp_str not in found:
                    found.append(temp_str)
        return found

    def extract_yields(self, text: str) -> list[str]:
        found = []
        for pattern in self.yield_patterns:
            for match in pattern.finditer(text):
                yield_str = match.group(0).strip()
                if yield_str not in found:
                    found.append(yield_str)
        return found

    def extract_times(self, text: str) -> list[str]:
        found = []
        for pattern in self.time_patterns:
            for match in pattern.finditer(text):
                time_str = match.group(0).strip()
                if time_str not in found:
                    found.append(time_str)
        return found

    def extract_pressures(self, text: str) -> list[str]:
        found = []
        for pattern in self.pressure_patterns:
            for match in pattern.finditer(text):
                pressure_str = match.group(0).strip()
                if pressure_str not in found:
                    found.append(pressure_str)
        return found

    def extract_molecules(self, text: str) -> list[str]:
        found = []

        for match in self.common_molecule_pattern.finditer(text):
            name = match.group(0).strip()
            if name not in found:
                found.append(name)

        for match in self.iupac_pattern.finditer(text):
            name = match.group(0).strip()
            if name not in found and len(name) > 4:
                found.append(name)

        smiles_pattern = re.compile(r"\b([A-Za-z0-9@\+\-\[\]\(\)=#/\\\.]{5,100})\b")
        for match in smiles_pattern.finditer(text):
            candidate = match.group(1)
            if any(c in candidate for c in ["(", "=", "#"]) and not candidate.startswith("http"):
                from rdkit import Chem
                mol = Chem.MolFromSmiles(candidate)
                if mol is not None:
                    if candidate not in found:
                        found.append(candidate)

        return found

    def extract_all(self, text: str) -> dict:
        return {
            "molecules": self.extract_molecules(text),
            "catalysts": self.extract_catalysts(text),
            "solvents": self.extract_solvents(text),
            "temperatures": self.extract_temperatures(text),
            "yields": self.extract_yields(text),
            "reaction_times": self.extract_times(text),
            "pressures": self.extract_pressures(text),
        }

    def extract_experimental_conditions(self, text: str) -> dict:
        catalysts = self.extract_catalysts(text)
        solvents = self.extract_solvents(text)
        temperatures = self.extract_temperatures(text)
        yields = self.extract_yields(text)
        times = self.extract_times(text)
        pressures = self.extract_pressures(text)

        return {
            "catalyst": catalysts[0] if catalysts else None,
            "solvent": solvents[0] if solvents else None,
            "temperature": temperatures[0] if temperatures else None,
            "yield_value": yields[0] if yields else None,
            "reaction_time": times[0] if times else None,
            "pressure": pressures[0] if pressures else None,
            "all_catalysts": catalysts,
            "all_solvents": solvents,
            "all_temperatures": temperatures,
            "all_yields": yields,
            "all_times": times,
            "all_pressures": pressures,
        }


entity_extractor = ChemicalEntityExtractor()
