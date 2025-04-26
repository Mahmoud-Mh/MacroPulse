import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { WebSocketProvider } from './components/WebSocketManager';
import { SeriesSelector } from './components/SeriesSelector';
import { DataVisualizer } from './components/DataVisualizer';
import { Login } from './components/Login';
import './App.css';

const Dashboard = () => {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" />;

  return (
    <WebSocketProvider token={token}>
      <div className="app">
        <header>
          <h1>MacroPulse Economic Data</h1>
        </header>
        <main>
          <div className="sidebar">
            <SeriesSelector />
          </div>
          <div className="content">
            <DataVisualizer />
          </div>
        </main>
      </div>
    </WebSocketProvider>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
