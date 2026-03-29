import { useCallback, useEffect, useState } from 'react';
import { listItems } from '../api/endpoints';
import type { Item } from '../types';

export function useItems(category?: string) {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setLoading(true);
    listItems(category)
      .then(setItems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [category]);

  useEffect(() => { refresh(); }, [refresh]);

  return { items, loading, error, refresh };
}
