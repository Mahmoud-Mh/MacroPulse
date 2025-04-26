import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f3f4f6',
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
  success: {
    color: '#059669',
    background: '#ecfdf5',
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
    background: '#6366f1',
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

export const SignUp = () => {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState<string | string[]>('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (form.password !== form.password2) {
      setError(["Passwords do not match"]);
      return;
    }
    try {
      await axios.post('http://127.0.0.1:8000/api/auth/register/', form);
      setSuccess('Registration successful! You can now log in.');
      setTimeout(() => navigate('/login'), 1200);
    } catch (err: any) {
      const data = err?.response?.data;
      if (data && typeof data === 'object') {
        // Flatten all error arrays into a single array of strings
        const messages = Object.values(data)
          .flat()
          .map((msg) => String(msg));
        setError(messages);
      } else {
        setError(['Registration failed. Please check your input.']);
      }
      console.log('Registration error:', data);
    }
  };

  const friendlyError = (msg: string) => {
    if (msg === 'This field must be unique.') return 'An account with this email already exists.';
    if (msg === 'A user with that username already exists.') return 'This username is already taken.';
    return msg;
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.title}>Create Your Account</div>
        {Array.isArray(error) && error.length > 0 && (
          <div style={styles.error}>
            {error.map((msg, idx) => (
              <div key={idx}>{friendlyError(msg)}</div>
            ))}
          </div>
        )}
        {typeof error === 'string' && error && (
          <div style={styles.error}>{error}</div>
        )}
        {success && <div style={styles.success}>{success}</div>}
        <form onSubmit={handleSubmit} style={styles.form} autoComplete="on">
          <div style={styles.group}>
            <label htmlFor="username" style={styles.label}>Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="username"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="email" style={styles.label}>Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="email"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="first_name" style={styles.label}>First Name</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="given-name"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="last_name" style={styles.label}>Last Name</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="family-name"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="password" style={styles.label}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="new-password"
            />
          </div>
          <div style={styles.group}>
            <label htmlFor="password2" style={styles.label}>Confirm Password</label>
            <input
              type="password"
              id="password2"
              name="password2"
              value={form.password2}
              onChange={handleChange}
              required
              style={styles.input}
              autoComplete="new-password"
            />
          </div>
          <button type="submit" style={styles.button}>Sign Up</button>
        </form>
        <Link to="/login" style={styles.link}>
          Already have an account? Log in
        </Link>
      </div>
    </div>
  );
}; 