import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f3f4f6', // soft gray
  },
  card: {
    background: 'white',
    borderRadius: '1rem',
    boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
    padding: '2.5rem 2rem',
    minWidth: '340px',
    maxWidth: '90vw',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#22223b',
    marginBottom: '1.5rem',
    letterSpacing: '0.01em',
    textAlign: 'center' as const,
  },
  error: {
    color: '#dc2626',
    background: '#fef2f2',
    borderRadius: '0.375rem',
    padding: '0.75rem 1rem',
    marginBottom: '1rem',
    width: '100%',
    textAlign: 'center' as const,
    fontSize: '0.95rem',
  },
  form: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.25rem',
  },
  group: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  label: {
    fontWeight: 500,
    color: '#4b5563',
    fontSize: '0.95rem',
  },
  input: {
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #e5e7eb',
    fontSize: '1rem',
    background: '#f9fafb',
    color: '#22223b',
    outline: 'none',
    transition: 'border 0.2s',
  },
  button: {
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: 'none',
    background: '#6366f1', // soft indigo accent
    color: 'white',
    fontWeight: 600,
    fontSize: '1.1rem',
    cursor: 'pointer',
    marginTop: '0.5rem',
    transition: 'background 0.2s',
    boxShadow: '0 1px 2px rgba(99,102,241,0.08)',
  },
  link: {
    marginTop: '1.5rem',
    color: '#6366f1',
    textDecoration: 'none',
    fontWeight: 500,
    fontSize: '1rem',
    textAlign: 'center' as const,
    display: 'block',
  },
};

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/auth/token/', {
        username,
        password
      });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Invalid credentials');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.title}>MacroPulse<br />Sign In</div>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleLogin} style={styles.form} autoComplete="on">
          <div style={styles.group}>
            <label htmlFor="username" style={styles.label}>Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={styles.input}
              autoComplete="username"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="password" style={styles.label}>Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
              autoComplete="current-password"
            />
          </div>
          <button type="submit" style={styles.button}>Login</button>
        </form>
        <Link to="/signup" style={styles.link}>
          Don't have an account? Sign up
        </Link>
      </div>
    </div>
  );
}; 