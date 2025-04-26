import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import Chart from 'chart.js/auto';
import './EconomicData.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const EconomicData = () => {
  const [seriesData, setSeriesData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!searchTerm) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/ws/economic-data/search?term=${encodeURIComponent(searchTerm)}`);
      const data = await response.json();
      setSearchResults(data.series || []);
    } catch (err) {
      setError('Failed to fetch search results');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeriesSelect = async (seriesId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/ws/economic-data/series/${seriesId}`);
      const data = await response.json();
      setSeriesData(data);
    } catch (err) {
      setError('Failed to fetch series data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const chartData = seriesData ? {
    labels: seriesData.observations.map(obs => obs.date),
    datasets: [
      {
        label: seriesData.title,
        data: seriesData.observations.map(obs => parseFloat(obs.value)),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  } : null;

  const chartOptions = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'month'
        }
      },
      y: {
        beginAtZero: true
      }
    }
  };

  return (
    <div className="economic-data-container">
      <h2>Economic Data Explorer</h2>
      
      <div className="search-section">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search for economic data series..."
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h3>Search Results</h3>
          <ul>
            {searchResults.map((series) => (
              <li key={series.id}>
                <button onClick={() => handleSeriesSelect(series.id)}>
                  {series.title}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {seriesData && (
        <div className="series-data">
          <h3>{seriesData.title}</h3>
          <p>{seriesData.description}</p>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}
    </div>
  );
};

export default EconomicData; 