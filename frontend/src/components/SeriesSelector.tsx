import { useState } from 'react';
import { useWebSocket } from './WebSocketManager';

export const SeriesSelector = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeries, setSelectedSeries] = useState('');
  const { sendMessage, lastMessage } = useWebSocket();

  const handleSearch = () => {
    if (searchTerm.trim()) {
      sendMessage({
        type: 'search_series',
        search_term: searchTerm
      });
    }
  };

  const handleSeriesSelect = (seriesId: string) => {
    setSelectedSeries(seriesId);
    sendMessage({
      type: 'get_series',
      series_id: seriesId
    });
  };

  const searchResults = lastMessage?.type === 'search_results' ? lastMessage.results.series : [];

  return (
    <div className="series-selector">
      <div className="search-box">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search for economic indicators..."
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {searchResults.length > 0 && (
        <div className="search-results">
          <h3>Search Results</h3>
          <ul>
            {searchResults.map((series: any) => (
              <li
                key={series.id}
                className={selectedSeries === series.id ? 'selected' : ''}
                onClick={() => handleSeriesSelect(series.id)}
              >
                <div className="series-title">{series.title}</div>
                <div className="series-id">{series.id}</div>
                <div className="series-frequency">{series.frequency}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}; 