import { useEffect, useState } from 'react';
import { getPortfolioSummary } from '../api/endpoints';
import type { PortfolioSummary } from '../types';

export function usePortfolio(days = 365) {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPortfolioSummary(days)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, [days]);

  return { summary, loading };
}
