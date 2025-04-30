import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { Login } from './components/Login';
import { SignUp } from './components/SignUp';
import { WebSocketProvider } from './components/WebSocketManager';
import { DataVisualizer } from './components/DataVisualizer';
import MonitoringDashboard from './components/MonitoringDashboard';
import TaskManager from './components/TaskManager';
import './App.css';

const styles = {
  root: {
    margin: 0,
    padding: 0,
    width: '100vw',
    height: '100vh',
    overflow: 'hidden',
  },
  nav: {
    backgroundColor: '#f8f9fa',
    padding: '10px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  navLinks: {
    display: 'flex',
    gap: '20px',
  },
  navLink: {
    textDecoration: 'none',
    color: '#333',
    padding: '8px 16px',
    borderRadius: '4px',
    transition: 'all 0.3s ease',
  },
  navLinkActive: {
    backgroundColor: '#e9ecef',
    color: '#007bff',
  },
  content: {
    padding: '20px',
    height: 'calc(100vh - 60px)',
    overflow: 'auto',
  },
};

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link 
      to={to} 
      style={{
        ...styles.navLink,
        ...(isActive ? styles.navLinkActive : {})
      }}
    >
      {children}
    </Link>
  );
}

function Dashboard() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" />;
  }

  return (
    <WebSocketProvider>
      <div style={styles.root}>
        <nav style={styles.nav}>
          <div style={styles.navLinks}>
            <NavLink to="/dashboard">Data Visualizer</NavLink>
            <NavLink to="/monitoring">System Status</NavLink>
            <NavLink to="/task-manager">Task Manager</NavLink>
          </div>
        </nav>
        <div style={styles.content}>
          <DataVisualizer />
        </div>
      </div>
    </WebSocketProvider>
  );
}

function Monitoring() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" />;
  }

  return (
    <div style={styles.root}>
      <nav style={styles.nav}>
        <div style={styles.navLinks}>
          <NavLink to="/dashboard">Data Visualizer</NavLink>
          <NavLink to="/monitoring">System Status</NavLink>
          <NavLink to="/task-manager">Task Manager</NavLink>
        </div>
      </nav>
      <div style={styles.content}>
        <MonitoringDashboard />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/task-manager" element={<TaskManager />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}
