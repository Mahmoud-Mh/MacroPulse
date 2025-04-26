import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './components/Login';
import { WebSocketProvider } from './components/WebSocketManager';
import { DataVisualizer } from './components/DataVisualizer';

const styles = {
  root: {
    margin: 0,
    padding: 0,
    width: '100vw',
    height: '100vh',
    overflow: 'hidden',
  },
};

function Dashboard() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" />;
  }

  return (
    <WebSocketProvider>
      <div style={styles.root}>
        <DataVisualizer />
      </div>
    </WebSocketProvider>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}
