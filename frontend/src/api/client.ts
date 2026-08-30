import type {
  SearchResponse,
  PaperListResponse,
  IngestResponse,
  MoleculeConvertResponse,
  GraphStats,
  ReactionInfo,
  EvaluationResults,
} from '../types';

const API_BASE = 'http://localhost:8000/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  search: async (question: string, maxResults: number = 8): Promise<SearchResponse> => {
    return fetchJson<SearchResponse>(`${API_BASE}/search`, {
      method: 'POST',
      body: JSON.stringify({ question, max_results: maxResults }),
    });
  },

  listPapers: async (skip = 0, limit = 20, search?: string): Promise<PaperListResponse> => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (search) params.set('search', search);
    return fetchJson<PaperListResponse>(`${API_BASE}/papers?${params}`);
  },

  ingestPaper: async (formData: FormData): Promise<IngestResponse> => {
    const response = await fetch(`${API_BASE}/papers/ingest`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  },

  deletePaper: async (paperId: number): Promise<void> => {
    await fetchJson(`${API_BASE}/papers/${paperId}`, { method: 'DELETE' });
  },

  convertMolecule: async (inputValue: string, inputType: string = 'name'): Promise<MoleculeConvertResponse> => {
    return fetchJson<MoleculeConvertResponse>(`${API_BASE}/chemistry/convert`, {
      method: 'POST',
      body: JSON.stringify({ input_value: inputValue, input_type: inputType }),
    });
  },

  getReactions: async (): Promise<ReactionInfo[]> => {
    return fetchJson<ReactionInfo[]>(`${API_BASE}/chemistry/reactions`);
  },

  getGraphStats: async (): Promise<GraphStats> => {
    return fetchJson<GraphStats>(`${API_BASE}/graph/stats`);
  },

  runEvaluation: async (): Promise<EvaluationResults> => {
    return fetchJson<EvaluationResults>(`${API_BASE}/evaluation/run`, { method: 'POST' });
  },

  getEvaluationResults: async (): Promise<EvaluationResults> => {
    return fetchJson<EvaluationResults>(`${API_BASE}/evaluation/results`);
  },
};
