import io
import base64
from typing import Optional
from rdkit import Chem
from rdkit.Chem import (
    Descriptors,
    Draw,
    AllChem,
    Fragments,
    rdMolDescriptors,
    DataStructs,
)
from rdkit.Chem.Draw import rdMolDraw2D


COMMON_MOLECULES = {
    "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "acetylsalicylic acid": "CC(=O)Oc1ccccc1C(=O)O",
    "caffeine": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
    "ibuprofen": "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "paracetamol": "CC(=O)Nc1ccc(O)cc1",
    "acetaminophen": "CC(=O)Nc1ccc(O)cc1",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "ethanol": "CCO",
    "methanol": "CO",
    "acetic acid": "CC(=O)O",
    "acetone": "CC(=O)C",
    "dmf": "CN(C)C=O",
    "dimethylformamide": "CN(C)C=O",
    "thf": "C1CCOC1",
    "tetrahydrofuran": "C1CCOC1",
    "dmso": "CS(=O)C",
    "dimethyl sulfoxide": "CS(=O)C",
    "chloroform": "ClC(Cl)Cl",
    "dichloromethane": "ClCCl",
    "diethyl ether": "CCOCC",
    "hexane": "CCCCCC",
    "pentane": "CCCCC",
    "pyridine": "c1ccncc1",
    "aniline": "Nc1ccccc1",
    "phenol": "Oc1ccccc1",
    "naphthalene": "c1ccc2ccccc2c1",
    "glucose": "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
    "fructose": "OC[C@@H](O)[C@@H](O)[C@H](O)C(=O)CO",
    "sucrose": "OC[C@H]1OC(O[C@@]2(CO)OC[C@@H](O)[C@@H]2O)[C@H](O)[C@@H](O)[C@@H]1O",
    "cholesterol": "C[C@H](CCCC(C)C)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C)C",
    "nicotine": "CN1CCC[C@H]1c2cccnc2",
    "morphine": "CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@H]3[C@H]1C5",
    "dopamine": "NCCc1ccc(O)c(O)c1",
    "serotonin": "NCCc1c[nH]c2ccc(O)cc12",
    "adrenaline": "CNC[C@H](O)c1ccc(O)c(O)c1",
    "penicillin g": "O=C(O)[C@@H]1N2C(=O)[C@@H](NC(=O)Cc3ccccc3)[C@H]2SC1(C)C",
    "vitamin c": "OC[C@@H](O)[C@H]1OC(=O)C(O)=C1O",
    "ascorbic acid": "OC[C@@H](O)[C@H]1OC(=O)C(O)=C1O",
    "citric acid": "OC(=O)CC(O)(CC(=O)O)C(=O)O",
    "urea": "NC(=O)N",
    "glycine": "NCC(=O)O",
    "alanine": "C[C@@H](N)C(=O)O",
    "tryptophan": "N[C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
}


FUNCTIONAL_GROUP_SMARTS = {
    "hydroxyl": "[OX2H]",
    "carboxylic acid": "[CX3](=O)[OX2H1]",
    "amine (primary)": "[NX3;H2;!$(NC=O)]",
    "amine (secondary)": "[NX3;H1;!$(NC=O)]",
    "amine (tertiary)": "[NX3;H0;!$(NC=O)]",
    "amide": "[NX3][CX3](=[OX1])",
    "aldehyde": "[CX3H1](=O)[#6]",
    "ketone": "[#6][CX3](=O)[#6]",
    "ester": "[#6][CX3](=O)[OX2H0][#6]",
    "ether": "[OD2]([#6])[#6]",
    "nitro": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]",
    "nitrile": "[NX1]#[CX2]",
    "sulfoxide": "[$([#16X3]=[OX1]),$([#16X3+][OX1-])]",
    "sulfone": "[$([#16X4](=[OX1])=[OX1]),$([#16X4+2]([OX1-])[OX1-])]",
    "thiol": "[#16X2H]",
    "halide (F)": "[F]",
    "halide (Cl)": "[Cl]",
    "halide (Br)": "[Br]",
    "halide (I)": "[I]",
    "phosphate": "[$(P(=[OX1])([OX2H])(O)(O)),$(P(=[OX1])([OX2H])([OX2H])(O))]",
    "aromatic ring": "a1aaaaa1",
    "alkene": "[CX3]=[CX3]",
    "alkyne": "[CX2]#[CX2]",
    "epoxide": "[OX2r3]1[#6r3][#6r3]1",
    "lactone": "[#6][CX3](=O)[OX2][#6]",
    "anhydride": "[CX3](=[OX1])[OX2][CX3](=[OX1])",
    "imine": "[CX3;$([C]([#6])[#6]),$([CH][#6])]=[NX2][#6]",
    "sulfonamide": "[$([#16X4]([NX3])(=[OX1])(=[OX1])),$([#16X4+2]([NX3])([OX1-])([OX1-]))]",
}


class MoleculeService:
    def __init__(self):
        self.common_molecules = COMMON_MOLECULES
        self.functional_group_patterns = {}
        for name, smarts in FUNCTIONAL_GROUP_SMARTS.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern is not None:
                self.functional_group_patterns[name] = pattern

    def name_to_smiles(self, name: str) -> Optional[str]:
        normalized = name.strip().lower()
        if normalized in self.common_molecules:
            return self.common_molecules[normalized]
        return None

    def smiles_to_molecule(self, smiles: str) -> Optional[Chem.Mol]:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return mol

    def validate_smiles(self, smiles: str) -> bool:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None

    def get_molecular_properties(self, smiles: str) -> Optional[dict]:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return None

        return {
            "smiles": smiles,
            "canonical_smiles": Chem.MolToSmiles(mol),
            "molecular_formula": rdMolDescriptors.CalcMolFormula(mol),
            "molecular_weight": round(Descriptors.MolWt(mol), 4),
            "exact_mass": round(Descriptors.ExactMolWt(mol), 4),
            "logp": round(Descriptors.MolLogP(mol), 4),
            "tpsa": round(Descriptors.TPSA(mol), 4),
            "hbd": Descriptors.NumHDonors(mol),
            "hba": Descriptors.NumHAcceptors(mol),
            "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "ring_count": Descriptors.RingCount(mol),
            "aromatic_rings": Descriptors.NumAromaticRings(mol),
            "heavy_atom_count": Descriptors.HeavyAtomCount(mol),
            "num_atoms": mol.GetNumAtoms(),
            "formal_charge": Chem.GetFormalCharge(mol),
            "num_radical_electrons": Descriptors.NumRadicalElectrons(mol),
            "complexity": round(Descriptors.BertzCT(mol), 4),
        }

    def get_functional_groups(self, smiles: str) -> list[str]:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return []

        found_groups = []
        for name, pattern in self.functional_group_patterns.items():
            if mol.HasSubstructMatch(pattern):
                matches = mol.GetSubstructMatches(pattern)
                count = len(matches)
                if count > 1:
                    found_groups.append(f"{name} (x{count})")
                else:
                    found_groups.append(name)
        return found_groups

    def get_fragment_descriptors(self, smiles: str) -> dict:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return {}

        fragments = {}
        fragment_functions = {
            "carboxylic_acid": Fragments.fr_COO,
            "aldehyde": Fragments.fr_aldehyde,
            "ketone": Fragments.fr_ketone,
            "alcohol_OH": Fragments.fr_Al_OH,
            "aromatic_OH": Fragments.fr_Ar_OH,
            "amine": Fragments.fr_NH2,
            "amide": Fragments.fr_amide,
            "ester": Fragments.fr_ester,
            "ether": Fragments.fr_ether,
            "halogen": Fragments.fr_halogen,
            "nitro": Fragments.fr_nitro,
            "nitrile": Fragments.fr_nitrile,
            "sulfide": Fragments.fr_sulfide,
            "benzene": Fragments.fr_benzene,
            "furan": Fragments.fr_furan,
            "imidazole": Fragments.fr_imidazole,
            "pyridine": Fragments.fr_pyridine,
            "thiophene": Fragments.fr_thiophene,
            "lactone": Fragments.fr_lactone,
            "epoxide": Fragments.fr_epoxide,
        }

        for name, func in fragment_functions.items():
            count = func(mol)
            if count > 0:
                fragments[name] = count

        return fragments

    def get_extended_descriptors(self, smiles: str) -> Optional[dict]:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return None

        AllChem.Compute2DCoords(mol)

        return {
            "balaban_j": round(Descriptors.BalabanJ(mol), 4) if Descriptors.RingCount(mol) > 0 else None,
            "bertz_ct": round(Descriptors.BertzCT(mol), 4),
            "chi0": round(Descriptors.Chi0(mol), 4),
            "chi1": round(Descriptors.Chi1(mol), 4),
            "hall_kier_alpha": round(Descriptors.HallKierAlpha(mol), 4),
            "kappa1": round(Descriptors.Kappa1(mol), 4),
            "kappa2": round(Descriptors.Kappa2(mol), 4),
            "labute_asa": round(Descriptors.LabuteASA(mol), 4),
            "peoe_vsa": [round(v, 4) for v in Descriptors.PEOE_VSA1(mol)] if hasattr(Descriptors.PEOE_VSA1(mol), '__iter__') else round(Descriptors.PEOE_VSA1(mol), 4),
            "fraction_csp3": round(Descriptors.FractionCSP3(mol), 4),
            "num_spiro_atoms": rdMolDescriptors.CalcNumSpiroAtoms(mol),
            "num_bridgehead_atoms": rdMolDescriptors.CalcNumBridgeheadAtoms(mol),
        }

    def smiles_to_svg(self, smiles: str, width: int = 400, height: int = 300) -> Optional[str]:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return None

        AllChem.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.drawOptions().addAtomIndices = False
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg

    def smiles_to_png_base64(self, smiles: str, width: int = 400, height: int = 300) -> Optional[str]:
        mol = self.smiles_to_molecule(smiles)
        if mol is None:
            return None

        AllChem.Compute2DCoords(mol)
        img = Draw.MolToImage(mol, size=(width, height))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def calculate_similarity(self, smiles1: str, smiles2: str) -> Optional[dict]:
        mol1 = self.smiles_to_molecule(smiles1)
        mol2 = self.smiles_to_molecule(smiles2)
        if mol1 is None or mol2 is None:
            return None

        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)

        tanimoto = DataStructs.TanimotoSimilarity(fp1, fp2)
        dice = DataStructs.DiceSimilarity(fp1, fp2)

        return {
            "tanimoto_similarity": round(tanimoto, 4),
            "dice_similarity": round(dice, 4),
        }

    def get_full_analysis(self, smiles: str, name: Optional[str] = None) -> Optional[dict]:
        properties = self.get_molecular_properties(smiles)
        if properties is None:
            return None

        functional_groups = self.get_functional_groups(smiles)
        fragments = self.get_fragment_descriptors(smiles)
        svg = self.smiles_to_svg(smiles)

        return {
            "name": name,
            "smiles": properties["canonical_smiles"],
            "molecular_formula": properties["molecular_formula"],
            "molecular_weight": properties["molecular_weight"],
            "exact_mass": properties["exact_mass"],
            "logp": properties["logp"],
            "tpsa": properties["tpsa"],
            "hbd": properties["hbd"],
            "hba": properties["hba"],
            "rotatable_bonds": properties["rotatable_bonds"],
            "ring_count": properties["ring_count"],
            "aromatic_rings": properties["aromatic_rings"],
            "functional_groups": functional_groups,
            "fragment_descriptors": fragments,
            "svg": svg,
        }


molecule_service = MoleculeService()
