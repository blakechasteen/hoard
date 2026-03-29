import { useCallback, useEffect, useState } from 'react';
import { clearToken, hasToken } from '../api/client';
import { getMe } from '../api/endpoints';
import type { User } from '../types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(hasToken());

  useEffect(() => {
    if (!hasToken()) {
      setLoading(false);
      return;
    }
    getMe()
      .then((u) => {
        setUser(u);
        setAuthenticated(true);
      })
      .catch(() => {
        clearToken();
        setAuthenticated(false);
      })
      .finally(() => setLoading(false));
  }, [authenticated]);

  const onLogin = useCallback(() => setAuthenticated(true), []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setAuthenticated(false);
  }, []);

  return { user, loading, authenticated, onLogin, logout };
}
