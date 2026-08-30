from typing import Optional


REACTION_DATABASE = {
    "suzuki": {
        "name": "Suzuki Coupling",
        "reaction_type": "cross-coupling",
        "description": "Palladium-catalyzed cross-coupling between an organoboron compound and an organic halide to form a new C-C bond.",
        "typical_catalysts": ["Pd(PPh3)4", "Pd(dppf)Cl2", "Pd(OAc)2", "Pd2(dba)3", "PdCl2"],
        "typical_solvents": ["DMF", "THF", "Dioxane", "Toluene", "DME", "Water/DMF"],
        "typical_temperature_range": "60-110°C",
        "mechanism": "Oxidative addition → Transmetallation → Reductive elimination",
        "smarts": "[#6:1]-[#5]>>[#6:1]-[#6]",
        "keywords": ["suzuki", "boronic acid", "boronate", "organoboron", "cross-coupling", "c-c coupling"],
    },
    "heck": {
        "name": "Heck Reaction",
        "reaction_type": "cross-coupling",
        "description": "Palladium-catalyzed coupling of an aryl or vinyl halide with an alkene to form a substituted alkene.",
        "typical_catalysts": ["Pd(OAc)2", "PdCl2", "Pd(PPh3)4", "Pd2(dba)3"],
        "typical_solvents": ["DMF", "DMA", "NMP", "Acetonitrile"],
        "typical_temperature_range": "80-150°C",
        "mechanism": "Oxidative addition → Syn insertion → Beta-hydride elimination → Reductive elimination",
        "smarts": None,
        "keywords": ["heck", "mizoroki-heck", "olefination", "vinyl coupling"],
    },
    "grignard": {
        "name": "Grignard Reaction",
        "reaction_type": "organometallic addition",
        "description": "Nucleophilic addition of an organomagnesium halide (Grignard reagent) to a carbonyl compound.",
        "typical_catalysts": ["Mg", "MgBr2"],
        "typical_solvents": ["THF", "Diethyl ether", "Et2O"],
        "typical_temperature_range": "-78 to 25°C",
        "mechanism": "Nucleophilic addition to carbonyl",
        "smarts": None,
        "keywords": ["grignard", "organomagnesium", "rmgx", "rmgbr", "rmgcl"],
    },
    "wittig": {
        "name": "Wittig Reaction",
        "reaction_type": "olefination",
        "description": "Conversion of a carbonyl compound to an alkene using a phosphonium ylide.",
        "typical_catalysts": [],
        "typical_solvents": ["THF", "DME", "Toluene", "CH2Cl2"],
        "typical_temperature_range": "-78 to 67°C",
        "mechanism": "Ylide addition → Betaine → Oxaphosphetane → Retro [2+2]",
        "smarts": None,
        "keywords": ["wittig", "phosphonium ylide", "olefination", "triphenylphosphine"],
    },
    "aldol": {
        "name": "Aldol Condensation",
        "reaction_type": "condensation",
        "description": "Condensation of an enolizable carbonyl compound with another carbonyl to form a β-hydroxy carbonyl.",
        "typical_catalysts": ["NaOH", "LDA", "LHMDS", "Proline", "Ti(OiPr)4"],
        "typical_solvents": ["THF", "CH2Cl2", "Water", "MeOH"],
        "typical_temperature_range": "-78 to 25°C",
        "mechanism": "Enolization → Nucleophilic addition → Dehydration (if condensation)",
        "smarts": None,
        "keywords": ["aldol", "condensation", "enolate", "beta-hydroxy"],
    },
    "diels_alder": {
        "name": "Diels-Alder Reaction",
        "reaction_type": "cycloaddition",
        "description": "[4+2] cycloaddition between a conjugated diene and a dienophile to form a six-membered ring.",
        "typical_catalysts": ["AlCl3", "BF3·OEt2", "ZnCl2", "TiCl4"],
        "typical_solvents": ["Toluene", "CH2Cl2", "Neat", "THF"],
        "typical_temperature_range": "25-200°C",
        "mechanism": "Concerted [4+2] cycloaddition",
        "smarts": None,
        "keywords": ["diels-alder", "diels alder", "cycloaddition", "4+2", "diene", "dienophile"],
    },
    "sonogashira": {
        "name": "Sonogashira Coupling",
        "reaction_type": "cross-coupling",
        "description": "Palladium/copper-catalyzed coupling of a terminal alkyne with an aryl or vinyl halide.",
        "typical_catalysts": ["Pd(PPh3)2Cl2", "PdCl2", "CuI", "Pd(PPh3)4"],
        "typical_solvents": ["THF", "DMF", "Et3N", "DIPA", "Piperidine"],
        "typical_temperature_range": "25-80°C",
        "mechanism": "Oxidative addition → Transmetallation (Cu) → Reductive elimination",
        "smarts": None,
        "keywords": ["sonogashira", "alkyne coupling", "terminal alkyne", "copper co-catalyst"],
    },
    "buchwald_hartwig": {
        "name": "Buchwald-Hartwig Amination",
        "reaction_type": "cross-coupling",
        "description": "Palladium-catalyzed cross-coupling of an amine with an aryl halide to form a C-N bond.",
        "typical_catalysts": ["Pd2(dba)3", "Pd(OAc)2", "BINAP", "XPhos", "SPhos"],
        "typical_solvents": ["Toluene", "Dioxane", "DME", "THF"],
        "typical_temperature_range": "80-120°C",
        "mechanism": "Oxidative addition → Coordination → Deprotonation → Reductive elimination",
        "smarts": None,
        "keywords": ["buchwald", "hartwig", "amination", "c-n coupling", "aryl amination"],
    },
    "olefin_metathesis": {
        "name": "Olefin Metathesis",
        "reaction_type": "metathesis",
        "description": "Redistribution of alkene fragments by scission and regeneration of C=C double bonds using metal-carbene catalysts.",
        "typical_catalysts": ["Grubbs 1st gen", "Grubbs 2nd gen", "Hoveyda-Grubbs", "Schrock catalyst"],
        "typical_solvents": ["CH2Cl2", "Toluene", "THF", "DCE"],
        "typical_temperature_range": "25-110°C",
        "mechanism": "Chauvin mechanism: [2+2] cycloaddition → Metallacyclobutane → Retro [2+2]",
        "smarts": None,
        "keywords": ["metathesis", "olefin metathesis", "grubbs", "ring-closing metathesis", "rcm", "cross metathesis"],
    },
    "fischer_esterification": {
        "name": "Fischer Esterification",
        "reaction_type": "esterification",
        "description": "Acid-catalyzed condensation of a carboxylic acid with an alcohol to form an ester.",
        "typical_catalysts": ["H2SO4", "HCl", "p-TsOH", "BF3·OEt2"],
        "typical_solvents": ["Toluene", "Benzene", "Neat", "Dean-Stark"],
        "typical_temperature_range": "60-120°C",
        "mechanism": "Protonation → Nucleophilic addition → Proton transfer → Elimination of water",
        "smarts": None,
        "keywords": ["fischer", "esterification", "ester", "acid-catalyzed"],
    },
    "friedel_crafts": {
        "name": "Friedel-Crafts Reaction",
        "reaction_type": "electrophilic aromatic substitution",
        "description": "Lewis acid-catalyzed alkylation or acylation of aromatic compounds.",
        "typical_catalysts": ["AlCl3", "FeCl3", "BF3·OEt2", "ZnCl2", "SnCl4"],
        "typical_solvents": ["CH2Cl2", "CS2", "Nitrobenzene", "DCE"],
        "typical_temperature_range": "0-80°C",
        "mechanism": "Electrophile generation → Arenium ion → Rearomatization",
        "smarts": None,
        "keywords": ["friedel-crafts", "friedel crafts", "alkylation", "acylation", "electrophilic aromatic substitution"],
    },
    "williamson_ether": {
        "name": "Williamson Ether Synthesis",
        "reaction_type": "substitution",
        "description": "SN2 reaction of an alkoxide with an alkyl halide or sulfonate to form an ether.",
        "typical_catalysts": ["NaH", "KOH", "K2CO3", "NaOH"],
        "typical_solvents": ["THF", "DMF", "DMSO", "Acetone"],
        "typical_temperature_range": "25-80°C",
        "mechanism": "SN2 displacement",
        "smarts": None,
        "keywords": ["williamson", "ether synthesis", "alkoxide", "sn2"],
    },
}


class ReactionService:
    def __init__(self):
        self.reactions = REACTION_DATABASE

    def get_reaction_info(self, reaction_name: str) -> Optional[dict]:
        normalized = reaction_name.strip().lower().replace(" ", "_").replace("-", "_")
        for key, info in self.reactions.items():
            if normalized == key or normalized in info.get("keywords", []):
                return info
            if any(kw in normalized for kw in info.get("keywords", [])):
                return info
        return None

    def classify_reaction(self, text: str) -> list[dict]:
        text_lower = text.lower()
        matches = []

        for key, info in self.reactions.items():
            score = 0
            matched_keywords = []

            for keyword in info.get("keywords", []):
                if keyword in text_lower:
                    score += 1
                    matched_keywords.append(keyword)

            for catalyst in info.get("typical_catalysts", []):
                if catalyst.lower() in text_lower:
                    score += 0.5
                    matched_keywords.append(catalyst)

            if score > 0:
                matches.append({
                    "reaction_key": key,
                    "reaction_name": info["name"],
                    "reaction_type": info["reaction_type"],
                    "confidence": min(score / 3.0, 1.0),
                    "matched_keywords": matched_keywords,
                })

        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def get_all_reactions(self) -> list[dict]:
        return [
            {
                "key": key,
                "name": info["name"],
                "reaction_type": info["reaction_type"],
                "description": info["description"],
                "typical_catalysts": info["typical_catalysts"],
                "typical_solvents": info["typical_solvents"],
                "typical_temperature_range": info["typical_temperature_range"],
            }
            for key, info in self.reactions.items()
        ]

    def find_reactions_by_catalyst(self, catalyst: str) -> list[dict]:
        catalyst_lower = catalyst.strip().lower()
        results = []

        for key, info in self.reactions.items():
            for cat in info.get("typical_catalysts", []):
                if catalyst_lower in cat.lower():
                    results.append({
                        "reaction_key": key,
                        "reaction_name": info["name"],
                        "catalyst_match": cat,
                    })
                    break

        return results

    def find_reactions_by_type(self, reaction_type: str) -> list[dict]:
        type_lower = reaction_type.strip().lower()
        return [
            {
                "key": key,
                "name": info["name"],
                "reaction_type": info["reaction_type"],
                "description": info["description"],
            }
            for key, info in self.reactions.items()
            if type_lower in info["reaction_type"].lower()
        ]


reaction_service = ReactionService()
