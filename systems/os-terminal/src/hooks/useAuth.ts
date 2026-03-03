import { useState, useEffect, useCallback } from 'react';
import { getStoredToken, setStoredToken, clearStoredToken } from '../utils/auth';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated' | 'error';
export type LoginResult = 'success' | 'invalid' | 'rate_limited' | 'error';

interface UseAuthReturn {
  status: AuthStatus;
  login: (token: string) => Promise<LoginResult>;
  logout: () => void;
  retry: () => void;
}

export function useAuth(): UseAuthReturn {
  const [status, setStatus] = useState<AuthStatus>('loading');

  const checkAuth = useCallback(async () => {
    setStatus('loading');
    try {
      // Bare fetch — auth endpoints don't use Bearer headers
      const res = await fetch('/api/auth/status');
      if (!res.ok) throw new Error('Server error');
      const { authRequired } = await res.json();

      if (!authRequired) {
        setStatus('authenticated');
        return;
      }

      // Auth required — check stored token
      const token = getStoredToken();
      if (!token) {
        setStatus('unauthenticated');
        return;
      }

      // Bare fetch — sends token in body, not as Bearer header
      const validateRes = await fetch('/api/auth/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      if (!validateRes.ok) throw new Error('Validation error');
      const { valid } = await validateRes.json();

      if (valid) {
        setStatus('authenticated');
      } else {
        clearStoredToken();
        setStatus('unauthenticated');
      }
    } catch {
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (token: string): Promise<LoginResult> => {
    try {
      // Bare fetch — sends token in body for validation, not as Bearer header
      const res = await fetch('/api/auth/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      if (res.status === 429) {
        return 'rate_limited';
      }
      if (!res.ok) return 'error';
      const { valid } = await res.json();
      if (valid) {
        setStoredToken(token);
        setStatus('authenticated');
        return 'success';
      }
      return 'invalid';
    } catch {
      return 'error';
    }
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setStatus('unauthenticated');
  }, []);

  return { status, login, logout, retry: checkAuth };
}
