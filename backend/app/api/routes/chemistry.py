from fastapi import APIRouter, HTTPException
from app.schemas.chemistry import (
    MoleculeConvertRequest,
    MoleculeConvertResponse,
    MoleculeProperties,
    SimilarityRequest,
    SimilarityResponse,
    ReactionInfo,
)
from app.services.chemistry.molecule_service import molecule_service
from app.services.chemistry.reaction_service import reaction_service
from app.services.chemistry.entity_extractor import entity_extractor

router = APIRouter()


@router.post("/convert", response_model=MoleculeConvertResponse)
async def convert_molecule(request: MoleculeConvertRequest):
    smiles = None
    name = None

    if request.input_type == "name":
        name = request.input_value
        smiles = molecule_service.name_to_smiles(request.input_value)
        if not smiles:
            raise HTTPException(status_code=404, detail=f"Could not find SMILES for '{request.input_value}'")
    elif request.input_type == "smiles":
        smiles = request.input_value
        if not molecule_service.validate_smiles(smiles):
            raise HTTPException(status_code=400, detail=f"Invalid SMILES: '{request.input_value}'")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported input type: {request.input_type}")

    props = molecule_service.get_molecular_properties(smiles)
    if not props:
        raise HTTPException(status_code=500, detail="Failed to compute molecular properties")

    functional_groups = molecule_service.get_functional_groups(smiles)
    svg = molecule_service.smiles_to_svg(smiles)

    mol_props = MoleculeProperties(
        name=name,
        smiles=props["canonical_smiles"],
        molecular_formula=props["molecular_formula"],
        molecular_weight=props["molecular_weight"],
        exact_mass=props["exact_mass"],
        logp=props["logp"],
        tpsa=props["tpsa"],
        hbd=props["hbd"],
        hba=props["hba"],
        rotatable_bonds=props["rotatable_bonds"],
        ring_count=props["ring_count"],
        aromatic_rings=props["aromatic_rings"],
        functional_groups=functional_groups,
        svg=svg,
    )

    return MoleculeConvertResponse(
        input_value=request.input_value,
        input_type=request.input_type,
        smiles=props["canonical_smiles"],
        name=name,
        properties=mol_props,
        svg=svg,
    )


@router.post("/properties", response_model=MoleculeProperties)
async def get_properties(smiles: str):
    if not molecule_service.validate_smiles(smiles):
        raise HTTPException(status_code=400, detail=f"Invalid SMILES: '{smiles}'")

    props = molecule_service.get_molecular_properties(smiles)
    if not props:
        raise HTTPException(status_code=500, detail="Failed to compute properties")

    functional_groups = molecule_service.get_functional_groups(smiles)
    svg = molecule_service.smiles_to_svg(smiles)

    return MoleculeProperties(
        smiles=props["canonical_smiles"],
        molecular_formula=props["molecular_formula"],
        molecular_weight=props["molecular_weight"],
        exact_mass=props["exact_mass"],
        logp=props["logp"],
        tpsa=props["tpsa"],
        hbd=props["hbd"],
        hba=props["hba"],
        rotatable_bonds=props["rotatable_bonds"],
        ring_count=props["ring_count"],
        aromatic_rings=props["aromatic_rings"],
        functional_groups=functional_groups,
        svg=svg,
    )


@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    if not molecule_service.validate_smiles(request.smiles_1):
        raise HTTPException(status_code=400, detail=f"Invalid SMILES 1: '{request.smiles_1}'")
    if not molecule_service.validate_smiles(request.smiles_2):
        raise HTTPException(status_code=400, detail=f"Invalid SMILES 2: '{request.smiles_2}'")

    result = molecule_service.calculate_similarity(request.smiles_1, request.smiles_2)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to calculate similarity")

    return SimilarityResponse(
        smiles_1=request.smiles_1,
        smiles_2=request.smiles_2,
        tanimoto_similarity=result["tanimoto_similarity"],
        dice_similarity=result["dice_similarity"],
    )


@router.get("/render/{smiles:path}")
async def render_molecule(smiles: str, width: int = 400, height: int = 300):
    if not molecule_service.validate_smiles(smiles):
        raise HTTPException(status_code=400, detail=f"Invalid SMILES: '{smiles}'")

    svg = molecule_service.smiles_to_svg(smiles, width=width, height=height)
    if not svg:
        raise HTTPException(status_code=500, detail="Failed to render molecule")

    from fastapi.responses import Response
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/reactions")
async def list_reactions():
    return reaction_service.get_all_reactions()


@router.get("/reactions/{reaction_name}")
async def get_reaction(reaction_name: str):
    info = reaction_service.get_reaction_info(reaction_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Reaction '{reaction_name}' not found")
    return info


@router.post("/extract-entities")
async def extract_entities(text: str):
    entities = entity_extractor.extract_all(text)
    conditions = entity_extractor.extract_experimental_conditions(text)
    return {
        "entities": entities,
        "conditions": conditions,
    }


@router.get("/molecules")
async def list_known_molecules():
    return {name: smiles for name, smiles in molecule_service.common_molecules.items()}
