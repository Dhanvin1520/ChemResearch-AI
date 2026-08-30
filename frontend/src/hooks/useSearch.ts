import { useState, useCallback } from 'react';
import type { SearchResponse } from '../types';
import { api } from '../api/client';

export function useSearch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [history, setHistory] = useState<string[]>([]);

  const search = useCallback(async (question: string, maxResults: number = 8) => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.search(question, maxResults);
      setResult(response);
      setHistory(prev => {
        const updated = [question, ...prev.filter(q => q !== question)];
        return updated.slice(0, 20);
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Search failed';
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { search, loading, error, result, history, clear };
}
