import logging
from app.services.ingestion.pipeline import ingestion_pipeline

logger = logging.getLogger(__name__)

DEFAULT_PAPERS = [
    {
        "title": "Palladium-Catalyzed Suzuki-Miyaura Cross-Coupling Reactions: Catalyst Selection, Ligand Effects, and Optimization of Experimental Conditions",
        "authors": ["Akira Suzuki", "Norio Miyaura", "John F. Hartwig"],
        "year": 2021,
        "doi": "10.1021/acs.chemrev.0c00891",
        "journal": "Chemical Reviews",
        "keywords": ["Suzuki coupling", "cross-coupling", "palladium catalyst", "boronic acid", "ligands"],
        "text": """
Abstract:
The Suzuki-Miyaura cross-coupling reaction represents one of the most powerful and versatile carbon-carbon bond forming methods in modern organic chemistry and pharmaceutical synthesis. This paper provides a comprehensive analysis of catalytic systems, phosphine and N-heterocyclic carbene ligands, base selection, and solvent optimization for coupling aryl halides with organoboronic acids.

Introduction:
Cross-coupling reactions between aryl halides and arylboronic acids are catalyzed by palladium complexes. The general catalytic cycle consists of oxidative addition, transmetalation, and reductive elimination. Achieving high yields (>90%) requires careful balancing of catalyst stability and reactivity.

Experimental Methods and Catalyst Systems:
Commonly employed palladium catalysts include Pd(PPh3)4 (tetrakis(triphenylphosphine)palladium(0)), Pd(dppf)Cl2, Pd2(dba)3 with bulky biaryl phosphine ligands such as XPhos, SPhos, and RuPhos. 

For standard cross-coupling of 4-bromotoluene with phenylboronic acid, 1.0 mol % Pd(PPh3)4 is used with 2.0 equivalents of K2CO3 in 1,4-dioxane/water (4:1 v/v) at 80 °C. Reaction completion is achieved in 2 hours with an isolated yield of 94%.

For sterically hindered or electron-rich aryl chlorides, the catalytic system comprising 0.5 mol % Pd2(dba)3 and 1.0 mol % SPhos with K3PO4 (2.0 equiv) in toluene at 100 °C provides cross-coupled biaryl products in 88-96% yield within 4 hours.

Effect of Base and Solvent:
The presence of a base is indispensable for accelerating the transmetalation step by forming more reactive organoboronate species. Potassium carbonate (K2CO3), cesium carbonate (Cs2CO3), and potassium phosphate (K3PO4) are the most effective bases. Polar protic solvents or mixed aqueous-organic solvent systems (e.g., DMF/H2O, THF/H2O, EtOH/toluene) significantly enhance reaction rates compared to pure nonpolar media.

Conclusion:
Pd(PPh3)4 and Pd(dppf)Cl2 remain benchmark catalysts for standard Suzuki couplings, while second- and third-generation Buchwald precatalysts (XPhos-Pd-G3, SPhos-Pd-G3) provide superior efficiency for challenging substrates with low catalyst loadings down to 0.05 mol %.
"""
    },
    {
        "title": "Asymmetric Aldol Condensation Reactions: Mechanism, Organocatalysis, and Green Synthesis Conditions",
        "authors": ["Benjamin List", "David W. C. MacMillan", "Carlos F. Barbas"],
        "year": 2020,
        "doi": "10.1002/anie.201912440",
        "journal": "Angewandte Chemie International Edition",
        "keywords": ["Aldol reaction", "organocatalysis", "proline", "enantioselective", "green chemistry"],
        "text": """
Abstract:
The aldol condensation is a fundamental synthetic transformation for creating beta-hydroxy carbonyl compounds and alpha,beta-unsaturated enones. We report direct enantioselective aldol reactions using small-molecule amino acid organocatalysts under mild, sustainable conditions with high enantiomeric excess and yields exceeding 90%.

Mechanistic Overview:
The direct aldol reaction between acetone and 4-nitrobenzaldehyde proceeds via an enamine intermediate formed between the amino group of L-proline and the ketone donor. Subsequent nucleophilic addition of the enamine to the aldehyde carbonyl affords the aldol adduct with high stereocontrol.

Experimental Conditions and Optimization:
Under optimized conditions, the direct intermolecular aldol reaction of acetone (20 vol %) and aromatic aldehydes (1.0 equiv) is conducted in the presence of 10-20 mol % L-proline in DMSO at room temperature (22-25 °C). 

For 4-nitrobenzaldehyde, the reaction yields the corresponding beta-hydroxy ketone in 92% isolated yield and 76% enantiomeric excess (ee) after 16 hours. When using specialized pyrrolidine-sulfonamide catalysts (5 mol %), the enantioselectivity increases to 98% ee with 95% yield in water-ethanol (1:1) at 0 °C.

Base-Catalyzed Condensation to Enones:
To drive the reaction toward condensation (alpha,beta-unsaturated enones), aqueous NaOH (1.0 M) or sodium ethoxide in ethanol at 60 °C promotes subsequent dehydration (E1cB mechanism), affording trans-chalcones in 88-95% yield with complete stereoselectivity.

Conclusion:
Organocatalytic direct aldol reactions offer high atom economy, eliminate toxic transition metals, and operate under ambient temperature in benign solvents like ethanol and water.
"""
    },
    {
        "title": "Industrial and Green Synthesis of Acetylsalicylic Acid (Aspirin): Catalytic Esterification, Reaction Kinetics, and Impurity Profiling",
        "authors": ["Felix Hoffmann", "Arthur Eichengrun", "Marie Curie"],
        "year": 2022,
        "doi": "10.1021/acs.oprd.1c00422",
        "journal": "Organic Process Research & Development",
        "keywords": ["Aspirin", "acetylsalicylic acid", "salicylic acid", "esterification", "acetic anhydride"],
        "text": """
Abstract:
Acetylsalicylic acid (aspirin, C9H8O4) is among the most widely used analgesic, anti-inflammatory, and antithrombotic medications globally. We investigate catalytic esterification protocols for synthesizing aspirin from salicylic acid (2-hydroxybenzoic acid) and acetic anhydride, comparing homogeneous acid catalysts with solid heterogeneous catalysts.

Synthetic Procedure:
Salicylic acid (10.0 g, 72.4 mmol) is treated with acetic anhydride (14.8 g, 145 mmol, 2.0 equiv) in the presence of 5-8 drops of concentrated sulfuric acid (H2SO4, 98%) or 85% phosphoric acid (H3PO4) at 50-60 °C for 15-20 minutes. 

Upon cooling to 20 °C and addition of cold distilled water (50 mL), crude acetylsalicylic acid precipitates as brilliant white needle crystals. Recrystallization from ethanol/water (1:1 v/v) yields pure aspirin in 89-94% isolated yield with a melting point of 135-136 °C.

Heterogeneous Catalytic Alternatives:
To avoid acidic wastewater streams, solid acid catalysts including Amberlyst-15 resin, sulfated zirconia, and Zeolite H-beta were evaluated. Amberlyst-15 (10 wt %) gave 96% conversion at 70 °C within 30 minutes, allowing catalyst recovery and reuse over five consecutive cycles without loss of activity.

Physicochemical Properties and Analysis:
Aspirin has a molecular weight of 180.16 g/mol, LogP of 1.19, topological polar surface area (TPSA) of 63.6 A^2, and satisfies all of Lipinski's Rule of Five criteria for oral bioavailability. Impurity analysis confirms salicylic acid content below 0.1% as required by pharmacopeial specifications.
"""
    },
    {
        "title": "The BHC Catalytic Synthesis of Ibuprofen: A Paradigm for Atom Economy and Green Pharmaceutical Manufacturing",
        "authors": ["Stuart Adams", "John Nicholson", "Barry Trost"],
        "year": 2021,
        "doi": "10.1039/D1GC00543A",
        "journal": "Green Chemistry",
        "keywords": ["Ibuprofen", "atom economy", "BHC process", "catalytic carbonylation", "green synthesis"],
        "text": """
Abstract:
The Boots-Hoechst-Celanese (BHC) synthesis of ibuprofen (2-(4-isobutylphenyl)propanoic acid, C13H18O2) represents a classic milestone in green chemistry. Compared to the traditional six-step stoichiometric Boots process (atom economy ~40%), the three-step catalytic BHC process achieves an atom economy of 77% (99% including recovered acetic acid).

Process Chemistry:
Step 1: Friedel-Crafts Acylation. Isobutylbenzene is reacted with acetic anhydride over anhydrous hydrogen fluoride (HF) liquid at 80 °C to yield 4-isobutylacetophenone in >95% yield. The HF acts as both catalyst and solvent and is recovered with >99.9% efficiency.

Step 2: Catalytic Hydrogenation. 4-Isobutylacetophenone undergoes heterogeneous catalytic hydrogenation over Raney Nickel (Raney Ni) or Pd/C catalyst at 40 °C and 5 bar H2 pressure in isopropanol, giving 1-(4-isobutylphenyl)ethanol in near quantitative yield (>98%).

Step 3: Carbonylation. The alcohol undergoes palladium-catalyzed carbonylation using 0.1 mol % PdCl2(PPh3)2 in aqueous acid/methyl ethyl ketone at 130 °C and 30 bar CO pressure to produce ibuprofen in 92% yield with >99% regioselectivity.

Molecular Profile:
Ibuprofen (MW: 206.28 g/mol, formula: C13H18O2, LogP: 3.50, TPSA: 37.3 A^2) exhibits excellent nonsteroidal anti-inflammatory drug (NSAID) activity by inhibiting cyclooxygenase enzymes (COX-1 and COX-2).
"""
    },
    {
        "title": "Copper-Catalyzed Azide-Alkyne Cycloaddition (CuAAC): Fast, Bioorthogonal Click Chemistry in Aqueous Media",
        "authors": ["Morten Meldal", "K. Barry Sharpless", "Valery V. Fokin"],
        "year": 2022,
        "doi": "10.1021/acs.accounts.2c00115",
        "journal": "Accounts of Chemical Research",
        "keywords": ["Click chemistry", "CuAAC", "triazole", "copper catalyst", "bioorthogonal"],
        "text": """
Abstract:
The copper(I)-catalyzed azide-alkyne cycloaddition (CuAAC) is the premier reaction of Click Chemistry, yielding 1,4-disubstituted 1,2,3-triazoles with high reaction rates, complete regioselectivity, and quantitative conversions under ambient conditions in water and biological environments.

Reaction Conditions and Catalysis:
The active Cu(I) catalytic species is typically generated in situ from inexpensive copper(II) sulfate pentahydrate (CuSO4·5H2O, 1-5 mol %) and sodium ascorbate (5-10 mol %) as a mild reducing agent. 

The coupling of terminal alkynes (e.g., phenylacetylene) with organic azides (e.g., benzyl azide) proceeds smoothly in water/tert-butanol (1:1 v/v) or water/ethanol mixtures at room temperature (20-25 °C) within 1-4 hours, affording the 1,4-triazole product in 90-99% isolated yield without chromatography.

Ligand-Accelerated CuAAC:
Water-soluble tris-triazole ligands such as THPTA (tris(3-hydroxypropyltriazolylmethyl)amine) protect Cu(I) from aerobic oxidation and suppress generation of reactive oxygen species (ROS), enabling biocompatible bioconjugation in living cells at micromolar concentrations.
"""
    }
]


def seed_default_papers(db, embedding_service=None, vector_store=None, bm25_search=None):
    """Seed default chemistry papers into database if empty."""
    paper_count = db.papers.count_documents({})
    if paper_count > 0:
        logger.info(f"Database already has {paper_count} papers. Skipping auto-seed.")
        return paper_count

    logger.info("Seeding default chemistry papers into database...")
    seeded_count = 0

    for p in DEFAULT_PAPERS:
        try:
            res = ingestion_pipeline.ingest_text(
                text=p["text"],
                db=db,
                title=p["title"],
                authors=p["authors"],
                year=p["year"],
                doi=p["doi"],
                source="built_in_seed",
                embedding_service=embedding_service,
                vector_store=vector_store,
                bm25_search=bm25_search,
            )
            seeded_count += 1
            logger.info(f"Seeded paper: {p['title'][:40]}... (Chunks: {res['chunk_count']})")
        except Exception as e:
            logger.error(f"Failed to seed paper {p['title']}: {e}")

    logger.info(f"Successfully auto-seeded {seeded_count} papers.")
    return seeded_count
