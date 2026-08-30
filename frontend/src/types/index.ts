export interface Citation {
  citation_id: number;
  paper_title: string;
  paper_id: number;
  section: string;
  evidence_text: string;
  doi: string | null;
  year: number | null;
  relevance_score: number;
}

export interface Evidence {
  chunk_id: number;
  paper_id: number;
  paper_title: string;
  section: string;
  content: string;
  catalyst: string | null;
  solvent: string | null;
  temperature: string | null;
  yield_value: string | null;
  relevance_score: number;
  chemical_entities: string[];
}

export interface StructuredData {
  catalyst: string | null;
  solvent: string | null;
  temperature: string | null;
  yield_value: string | null;
  reaction: string | null;
  conditions: Record<string, string | null> | null;
  source_paper: string | null;
  source_section: string | null;
}

export interface MoleculeInfo {
  smiles: string;
  formula: string;
  molecular_weight: number;
  functional_groups: string[];
  svg: string | null;
}

export interface SearchResponse {
  question: string;
  answer: string;
  citations: Citation[];
  evidence: Evidence[];
  structured_data: StructuredData[];
  citation_score: number;
  total_claims: number;
  supported_claims: number;
  processing_time_ms: number;
  query_plan: Record<string, unknown> | null;
  molecule_info: Record<string, MoleculeInfo> | null;
}

export interface Paper {
  id: number;
  title: string;
  authors: string[] | null;
  year: number | null;
  abstract: string | null;
  doi: string | null;
  source: string | null;
  journal: string | null;
  keywords: string[] | null;
  chemical_entities: string[] | null;
  reactions: string[] | null;
  chunk_count: number | null;
  created_at: string | null;
}

export interface PaperListResponse {
  papers: Paper[];
  total: number;
}

export interface IngestResponse {
  paper_id: number;
  title: string;
  chunk_count: number;
  chemical_entities: string[];
  reactions: string[];
  message: string;
}

export interface MoleculeProperties {
  name: string | null;
  smiles: string;
  molecular_formula: string;
  molecular_weight: number;
  exact_mass: number;
  logp: number;
  tpsa: number;
  hbd: number;
  hba: number;
  rotatable_bonds: number;
  ring_count: number;
  aromatic_rings: number;
  functional_groups: string[];
  svg: string | null;
}

export interface MoleculeConvertResponse {
  input_value: string;
  input_type: string;
  smiles: string;
  name: string | null;
  properties: MoleculeProperties;
  svg: string | null;
}

export interface GraphStats {
  connected: boolean;
  node_counts: Record<string, number>;
  relationship_counts: Record<string, number>;
}

export interface ReactionInfo {
  name: string;
  reaction_type: string;
  description: string;
  typical_catalysts: string[];
  typical_solvents: string[];
  typical_temperature_range: string | null;
  mechanism: string | null;
}

export interface EvaluationResults {
  total_questions: number;
  total_time_seconds: number;
  avg_time_per_question_ms: number;
  metrics: Record<string, { mean: number; min: number; max: number; count: number }>;
  individual_results: Record<string, unknown>[];
}

export type TabType = 'search' | 'papers' | 'chemistry' | 'graph' | 'evaluation';
