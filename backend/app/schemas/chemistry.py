from pydantic import BaseModel, Field
from typing import Optional


class MoleculeConvertRequest(BaseModel):
    input_value: str = Field(..., min_length=1)
    input_type: str = Field(default="name", pattern="^(name|smiles|inchi)$")


class MoleculeProperties(BaseModel):
    name: Optional[str] = None
    smiles: str
    molecular_formula: str
    molecular_weight: float
    exact_mass: float
    logp: float
    tpsa: float
    hbd: int
    hba: int
    rotatable_bonds: int
    ring_count: int
    aromatic_rings: int
    functional_groups: list[str] = []
    svg: Optional[str] = None


class MoleculeConvertResponse(BaseModel):
    input_value: str
    input_type: str
    smiles: str
    name: Optional[str] = None
    properties: MoleculeProperties
    svg: Optional[str] = None


class SimilarityRequest(BaseModel):
    smiles_1: str
    smiles_2: str


class SimilarityResponse(BaseModel):
    smiles_1: str
    smiles_2: str
    tanimoto_similarity: float
    dice_similarity: float
    common_substructure: Optional[str] = None


class ReactionInfo(BaseModel):
    name: str
    reaction_type: str
    description: str
    typical_catalysts: list[str] = []
    typical_solvents: list[str] = []
    typical_temperature_range: Optional[str] = None
    mechanism: Optional[str] = None
    smarts: Optional[str] = None
