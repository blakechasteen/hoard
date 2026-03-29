import { useState } from 'react';
import { login, register } from '../api/endpoints';

interface Props {
  onLogin: () => void;
}

export function LoginPage({ onLogin }: Props) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      if (isRegister) {
        await register(username, displayName, password, inviteCode);
      } else {
        await login(username, password);
      }
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Hoard</h1>
        <p className="login-subtitle">Track your collectibles like a portfolio</p>

        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>

          {isRegister && (
            <>
              <label>
                Display Name
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  required
                />
              </label>
              <label>
                Invite Code
                <input
                  type="text"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value)}
                  required
                />
              </label>
            </>
          )}

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={submitting} className="btn-primary btn-full">
            {submitting ? '...' : isRegister ? 'Register' : 'Log In'}
          </button>
        </form>

        <button
          className="btn-link"
          onClick={() => { setIsRegister(!isRegister); setError(''); }}
        >
          {isRegister ? 'Already have an account? Log in' : 'Need an account? Register'}
        </button>
      </div>
    </div>
  );
}
