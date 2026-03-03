import { useState, useCallback } from 'react';
import type { LoginResult } from '../hooks/useAuth';

interface LoginScreenProps {
  onLogin: (token: string) => Promise<LoginResult>;
}

const ERROR_MESSAGES: Record<string, string> = {
  invalid: 'Invalid token',
  rate_limited: 'Too many attempts. Try again in a minute.',
  error: 'Connection error. Try again.',
};

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim() || loading) return;

    setError('');
    setLoading(true);
    const result = await onLogin(token.trim());
    setLoading(false);

    if (result !== 'success') {
      setError(ERROR_MESSAGES[result] || 'Unknown error');
      if (result === 'invalid') setToken('');
    }
  }, [token, loading, onLogin]);

  return (
    <div className="login-screen">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1 className="login-title">OS Terminal</h1>
        <input
          type="password"
          autoComplete="current-password"
          inputMode="text"
          placeholder="Enter access token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="login-input"
          autoFocus
          disabled={loading}
        />
        <button type="submit" className="login-btn" disabled={loading || !token.trim()}>
          {loading ? 'Validating...' : 'Connect'}
        </button>
        {error && <div className="login-error">{error}</div>}
      </form>
    </div>
  );
}

export function ErrorScreen({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="login-screen">
      <div className="login-form">
        <h1 className="login-title">OS Terminal</h1>
        <div className="login-error">Server unreachable</div>
        <button className="login-btn" onClick={onRetry}>Retry</button>
      </div>
    </div>
  );
}
