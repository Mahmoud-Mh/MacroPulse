import { WebSocketProvider } from './components/WebSocketManager';
import { SeriesSelector } from './components/SeriesSelector';
import { DataVisualizer } from './components/DataVisualizer';
import './App.css';

function App() {
  // Replace this with your actual token
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1NjgyOTQxLCJpYXQiOjE3NDU2NzkzNDEsImp0aSI6IjYwMjRlYjZlZjhmZTQwMTA5N2JmODdkMzA1MjczY2MyIiwidXNlcl9pZCI6MzZ9.kiXShTXw73n9wagLp_Np3bUhNTkBqAbR9hd18ZBNhws';

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
}

export default App;
