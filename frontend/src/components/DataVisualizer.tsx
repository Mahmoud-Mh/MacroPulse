import { useEffect, useState } from 'react';
import { 
  LineChart, 
  BarChart, 
  AreaChart, 
  ComposedChart,
  PieChart,
  ScatterChart,
  RadarChart,
  Line, 
  Bar, 
  Area,
  Pie,
  Scatter,
  Radar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  Cell,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ReferenceArea,
} from 'recharts';
import { useWebSocket } from './WebSocketManager';

type ChartType = 'line' | 'bar' | 'area' | 'composed' | 'pie' | 'scatter' | 'radar';

interface DataPoint {
  date: string;
  value: number;
  movingAverage?: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
    width: '100%',
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#1e293b',
    padding: '1rem',
    color: 'white',
  },
  headerTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    margin: 0,
    textAlign: 'center' as const,
  },
  mainContent: {
    display: 'grid',
    gridTemplateColumns: '300px 1fr',
    gap: '1rem',
    padding: '1rem',
    height: 'calc(100vh - 4rem)',
    overflow: 'hidden',
  },
  sidebar: {
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    padding: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    height: '100%',
    overflow: 'auto',
  },
  searchSection: {
    display: 'flex',
    gap: '0.5rem',
  },
  searchInput: {
    flex: 1,
    padding: '0.5rem',
    borderRadius: '0.375rem',
    border: '1px solid #e2e8f0',
    fontSize: '0.875rem',
    backgroundColor: '#f8fafc',
    color: '#1e293b',
    '&:focus': {
      outline: 'none',
      borderColor: '#3b82f6',
      boxShadow: '0 0 0 1px #3b82f6',
    },
  },
  searchButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '0.375rem',
    fontSize: '0.875rem',
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: '#2563eb',
    },
  },
  visualizationSection: {
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    padding: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    height: '100%',
    overflow: 'auto',
  },
  visualizationHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem',
    borderBottom: '1px solid #e2e8f0',
  },
  visualizationTitle: {
    fontSize: '1rem',
    fontWeight: '500',
    color: '#1e293b',
    margin: 0,
  },
  controls: {
    display: 'flex',
    gap: '1rem',
    padding: '0.5rem',
    flexWrap: 'wrap' as const,
  },
  controlGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.25rem',
    minWidth: '150px',
  },
  label: {
    fontSize: '0.75rem',
    fontWeight: '500',
    color: '#64748b',
  },
  select: {
    padding: '0.375rem 0.5rem',
    borderRadius: '0.375rem',
    border: '1px solid #e2e8f0',
    fontSize: '0.875rem',
    backgroundColor: 'white',
    color: '#1e293b',
    cursor: 'pointer',
    '&:focus': {
      outline: 'none',
      borderColor: '#3b82f6',
      boxShadow: '0 0 0 1px #3b82f6',
    },
  },
  checkbox: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  checkboxInput: {
    width: '1rem',
    height: '1rem',
    cursor: 'pointer',
  },
  chartContainer: {
    flex: 1,
    minHeight: '400px',
    backgroundColor: '#f8fafc',
    borderRadius: '0.375rem',
    padding: '1rem',
  },
  errorMessage: {
    color: '#dc2626',
    backgroundColor: '#fef2f2',
    padding: '0.75rem',
    borderRadius: '0.375rem',
    fontSize: '0.875rem',
    textAlign: 'center' as const,
  },
  loadingMessage: {
    color: '#64748b',
    textAlign: 'center' as const,
    padding: '0.75rem',
    fontSize: '0.875rem',
  },
  searchResults: {
    marginTop: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  searchResultItem: {
    padding: '0.75rem',
    backgroundColor: 'white',
    borderRadius: '0.375rem',
    border: '1px solid #e2e8f0',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: '#f1f5f9',
      borderColor: '#3b82f6',
    },
  },
  seriesList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
    marginTop: '1rem',
    overflowY: 'auto' as const,
  },
  seriesItem: {
    padding: '0.75rem',
    backgroundColor: 'white',
    borderRadius: '0.375rem',
    border: '1px solid #e2e8f0',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: '#f1f5f9',
      borderColor: '#3b82f6',
    },
  },
  seriesTitle: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#1e293b',
  },
  seriesId: {
    fontSize: '0.75rem',
    color: '#64748b',
    marginTop: '0.25rem',
  },
  noResults: {
    padding: '1rem',
    textAlign: 'center' as const,
    color: '#64748b',
    fontSize: '0.875rem',
  },
  '@keyframes spin': {
    '0%': { transform: 'rotate(0deg)' },
    '100%': { transform: 'rotate(360deg)' }
  }
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  units?: string;
}

const CustomTooltip = ({ active, payload, label, units }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const date = new Date(label as string);
    const formattedDate = new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);

    return (
      <div style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        padding: '0.75rem',
        border: '1px solid #e2e8f0',
        borderRadius: '0.375rem',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{ margin: '0 0 0.5rem', fontWeight: '500', color: '#1e293b' }}>{formattedDate}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ margin: '0.25rem 0', color: entry.color }}>
            {entry.name}: {entry.value.toLocaleString()} {units}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const DataVisualizer = () => {
  const { lastMessage, sendMessage } = useWebSocket();
  const [chartData, setChartData] = useState<DataPoint[]>([]);
  const [chartType, setChartType] = useState<ChartType>('line');
  const [timeRange, setTimeRange] = useState<string>('all');
  const [showMovingAverage, setShowMovingAverage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [title, setTitle] = useState<string>('');
  const [units, setUnits] = useState<string>('');
  const [frequency, setFrequency] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [rawData, setRawData] = useState<DataPoint[]>([]);
  const availableSeries = [
    { id: 'GDP', title: 'Gross Domestic Product' },
    { id: 'UNRATE', title: 'Unemployment Rate' },
    { id: 'CPIAUCSL', title: 'Consumer Price Index' },
    { id: 'FEDFUNDS', title: 'Federal Funds Rate' },
    { id: 'DFF', title: 'Effective Federal Funds Rate' },
    { id: 'T10Y2Y', title: '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity' },
    { id: 'MORTGAGE30US', title: '30-Year Fixed Rate Mortgage Average' },
    { id: 'DCOILWTICO', title: 'Crude Oil Prices: WTI' },
    { id: 'DEXUSEU', title: 'USD/EUR Exchange Rate' },
    { id: 'SP500', title: 'S&P 500 Index' },
  ];
  const [filteredSeries, setFilteredSeries] = useState(availableSeries);
  const [zoomDomain, setZoomDomain] = useState<{ start: string | null; end: string | null }>({ start: null, end: null });
  const [selecting, setSelecting] = useState(false);
  const [selectionStart, setSelectionStart] = useState<string | null>(null);
  const [selectionEnd, setSelectionEnd] = useState<string | null>(null);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    if (term.trim()) {
      // First filter local list
      const localResults = availableSeries.filter(series => 
        series.title.toLowerCase().includes(term.toLowerCase()) ||
        series.id.toLowerCase().includes(term.toLowerCase())
      );
      
      // If we find local results, show them
      if (localResults.length > 0) {
        setFilteredSeries(localResults);
      } else {
        // If no local results, search via API
        sendMessage({ type: 'search_series', search_term: term });
      }
    } else {
      // If search is cleared, show all available series
      setFilteredSeries(availableSeries);
    }
  };

  const handleSeriesSelect = (seriesId: string) => {
    setIsLoading(true);
    setError(null);
    sendMessage({ type: 'get_series', series_id: seriesId });
  };

  const detectFrequency = (data: DataPoint[]): string => {
    if (data.length < 2) return '';
    
    // Sort dates to ensure we're comparing adjacent dates
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    // Check a few pairs to confirm consistency
    const sampleSize = Math.min(5, data.length - 1);
    const differences = Array.from({length: sampleSize}, (_, i) => {
      const curr = new Date(sortedData[i].date);
      const next = new Date(sortedData[i + 1].date);
      return Math.round((next.getTime() - curr.getTime()) / (1000 * 60 * 60 * 24));
    });

    // Get the most common difference
    const commonDiff = differences.reduce((a, b) => a + b, 0) / differences.length;

    if (commonDiff <= 1) return 'Daily';
    if (commonDiff <= 7) return 'Weekly';
    if (commonDiff >= 28 && commonDiff <= 31) return 'Monthly';
    if (commonDiff >= 90 && commonDiff <= 92) return 'Quarterly';
    if (commonDiff >= 365 && commonDiff <= 366) return 'Yearly';
    
    return 'Variable';
  };

  useEffect(() => {
    if (lastMessage?.type === 'series_data') {
      console.log('Received series data:', lastMessage);
      
      // Extract data from the series_data message
      const seriesData = lastMessage.data;
      console.log('Series data structure:', seriesData);
      
      if (!seriesData) {
        console.error('No data in series_data message');
        setError('No data received from the server');
        return;
      }

      // Check for API error messages
      if (seriesData.error) {
        console.error('API error:', seriesData.error);
        setError(seriesData.error);
        setRawData([]);
        return;
      }

      // Convert the series data to chart data format
      let data: DataPoint[] = [];
      if (seriesData.observations) {
        console.log('Raw observations:', seriesData.observations);
        data = seriesData.observations.map((observation: any) => {
          console.log('Processing observation:', observation);
          return {
            date: observation.date,
            value: parseFloat(observation.value)
          };
        }).filter((item: DataPoint) => {
          const isValid = !isNaN(item.value);
          if (!isValid) {
            console.log('Filtered out invalid value:', item);
          }
          return isValid;
        });

        // Set title and units from series data
        setTitle(seriesData.title || '');
        setUnits(seriesData.units || '');
        setFrequency(detectFrequency(data));
      } else {
        console.log('No observations found in series data');
        setError('No data available for this series');
        return;
      }

      if (data.length === 0) {
        setError('No valid data points found for this series');
        return;
      }

      setError(null);  // Clear any previous errors

      // Sort data by date
      data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      console.log('Sorted data:', data);

      // Apply time range filter
      if (timeRange !== 'all') {
        const now = new Date();
        const days = parseInt(timeRange);
        const oldData = [...data];
        data = data.filter((item: DataPoint) => {
          const itemDate = new Date(item.date);
          const shouldKeep = (now.getTime() - itemDate.getTime()) <= (days * 24 * 60 * 60 * 1000);
          if (!shouldKeep) {
            console.log('Filtered out date:', item.date);
          }
          return shouldKeep;
        });
        console.log(`Filtered data for time range ${timeRange}:`, data);
        console.log('Removed items:', oldData.length - data.length);
      }

      // Calculate moving average if enabled
      if (showMovingAverage) {
        data = data.map((item: DataPoint, index: number, array: DataPoint[]) => {
          const window = 5; // 5-point moving average
          const start = Math.max(0, index - Math.floor(window / 2));
          const end = Math.min(array.length, start + window);
          const windowData = array.slice(start, end);
          const avg = windowData.reduce((sum: number, d: DataPoint) => sum + d.value, 0) / windowData.length;
          return { ...item, movingAverage: avg };
        });
        console.log('Data with moving averages:', data);
      }

      console.log('Final processed chart data:', data);
      setRawData(data);
    }
  }, [lastMessage, timeRange, showMovingAverage]);

  useEffect(() => {
    if (lastMessage?.type === 'search_results') {
      const apiResults = lastMessage.results || [];
      setFilteredSeries(apiResults);
      setIsLoading(false);
    } else if (lastMessage?.type === 'series_data') {
      // Extract data from the series_data message
      const seriesData = lastMessage.data;
      
      if (!seriesData) {
        console.error('No data in series_data message');
        setError('No data received from the server');
        setIsLoading(false);
        return;
      }

      // Check for API error messages
      if (seriesData.error) {
        console.error('API error:', seriesData.error);
        setError(seriesData.error);
        setRawData([]);
        setIsLoading(false);
        return;
      }

      // Convert the series data to chart data format
      let data: DataPoint[] = [];
      if (seriesData.observations) {
        data = seriesData.observations.map((observation: any) => ({
          date: observation.date,
          value: parseFloat(observation.value)
        })).filter((item: DataPoint) => !isNaN(item.value));

        // Set title and units from series data
        setTitle(seriesData.title || '');
        setUnits(seriesData.units || '');
        setFrequency(detectFrequency(data));
      } else {
        setError('No data available for this series');
        setIsLoading(false);
        return;
      }

      if (data.length === 0) {
        setError('No valid data points found for this series');
        setIsLoading(false);
        return;
      }

      setError(null);
      // Sort data by date
      data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      setRawData(data);
      setIsLoading(false);
    }
  }, [lastMessage]);

  // Effect to handle time range and moving average changes
  useEffect(() => {
    if (rawData.length === 0) return;

    let filteredData = [...rawData];

    // Apply time range filter
    if (timeRange !== 'all') {
      const now = new Date();
      const days = parseInt(timeRange);
      filteredData = filteredData.filter(item => {
        const itemDate = new Date(item.date);
        return (now.getTime() - itemDate.getTime()) <= (days * 24 * 60 * 60 * 1000);
      });

      // Check if we have any data after filtering
      if (filteredData.length === 0) {
        setError(`No data available for the last ${days} days. Try a different time range.`);
        setChartData([]);
        return;
      }
    }

    // Clear any previous errors since we have data
    setError(null);

    // Calculate moving average if enabled
    if (showMovingAverage) {
      filteredData = filteredData.map((item, index, array) => {
        const window = 5; // 5-point moving average
        const start = Math.max(0, index - Math.floor(window / 2));
        const end = Math.min(array.length, start + window);
        const windowData = array.slice(start, end);
        const avg = windowData.reduce((sum, d) => sum + d.value, 0) / windowData.length;
        return { ...item, movingAverage: avg };
      });
    }

    setChartData(filteredData);
  }, [rawData, timeRange, showMovingAverage]);

  const handleMouseDown = (e: any) => {
    if (!e) return;
    setSelecting(true);
    setSelectionStart(e.activeLabel);
    setSelectionEnd(e.activeLabel);
  };

  const handleMouseMove = (e: any) => {
    if (!selecting || !e) return;
    setSelectionEnd(e.activeLabel);
  };

  const handleMouseUp = () => {
    if (!selecting) return;
    setSelecting(false);
    if (selectionStart && selectionEnd) {
      const startDate = new Date(selectionStart);
      const endDate = new Date(selectionEnd);
      if (startDate > endDate) {
        setZoomDomain({ start: selectionEnd, end: selectionStart });
      } else {
        setZoomDomain({ start: selectionStart, end: selectionEnd });
      }
    }
    setSelectionStart(null);
    setSelectionEnd(null);
  };

  const handleResetZoom = () => {
    setZoomDomain({ start: null, end: null });
  };

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 20, right: 30, left: 20, bottom: 5 }
    };

    // Filter data based on zoom domain
    const displayData = zoomDomain.start && zoomDomain.end
      ? chartData.filter(d => {
          const date = new Date(d.date);
          return date >= new Date(zoomDomain.start!) && date <= new Date(zoomDomain.end!);
        })
      : chartData;

    const commonChartProps = {
      onMouseDown: handleMouseDown,
      onMouseMove: handleMouseMove,
      onMouseUp: handleMouseUp,
      onMouseLeave: handleMouseUp
    };

    switch (chartType) {
      case 'line':
        return (
          <div style={{ width: '100%', height: '100%' }}>
            <ResponsiveContainer>
              <LineChart {...commonProps} {...commonChartProps} data={displayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip units={units} />} />
                <Legend />
                <Line type="monotone" dataKey="value" stroke={COLORS[0]} name="Value" dot={false} />
                {showMovingAverage && (
                  <Line type="monotone" dataKey="movingAverage" stroke={COLORS[1]} name="Moving Average" dot={false} />
                )}
                {selecting && selectionStart && selectionEnd && (
                  <ReferenceArea
                    x1={selectionStart}
                    x2={selectionEnd}
                    strokeOpacity={0.3}
                    fill="#3b82f6"
                    fillOpacity={0.3}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        );
      case 'bar':
        return (
          <div style={{ width: '100%', height: '100%' }}>
            <ResponsiveContainer>
              <BarChart {...commonProps} {...commonChartProps} data={displayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip units={units} />} />
                <Legend />
                <Bar dataKey="value" fill={COLORS[2]} name="Value" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );
      case 'area':
        return (
          <div style={{ width: '100%', height: '100%' }}>
            <ResponsiveContainer>
              <AreaChart {...commonProps} {...commonChartProps} data={displayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip units={units} />} />
                <Legend />
                <Area type="monotone" dataKey="value" stroke={COLORS[3]} fill={COLORS[3]} name="Value" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        );
      case 'composed':
        return (
          <ComposedChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="value" fill={COLORS[4]} stroke={COLORS[4]} name="Area" />
            <Bar dataKey="value" fill={COLORS[5]} name="Bar" />
            <Line type="monotone" dataKey="value" stroke={COLORS[6]} name="Line" />
          </ComposedChart>
        );
      case 'pie':
        return (
          <PieChart {...commonProps}>
            <Pie
              data={chartData.slice(-10)} // Show last 10 data points
              dataKey="value"
              nameKey="date"
              cx="50%"
              cy="50%"
              outerRadius={150}
              label
            >
              {chartData.slice(-10).map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        );
      case 'scatter':
        return (
          <ScatterChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Scatter data={chartData} fill={COLORS[0]} name="Value" />
          </ScatterChart>
        );
      case 'radar':
        return (
          <RadarChart {...commonProps} data={chartData.slice(-10)}>
            <PolarGrid />
            <PolarAngleAxis dataKey="date" />
            <PolarRadiusAxis />
            <Radar dataKey="value" stroke={COLORS[1]} fill={COLORS[1]} fillOpacity={0.6} name="Value" />
            <Legend />
            <Tooltip />
          </RadarChart>
        );
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>MacroPulse Economic Data</h1>
      </header>
      
      <main style={styles.mainContent}>
        <aside style={styles.sidebar}>
          <div style={styles.searchSection}>
            <input
              type="text"
              placeholder="Filter or search indicators..."
              style={styles.searchInput}
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>

          <div style={styles.seriesList}>
            {filteredSeries.map((series) => (
              <div
                key={series.id}
                style={styles.seriesItem}
                onClick={() => handleSeriesSelect(series.id)}
              >
                <div style={styles.seriesTitle}>{series.title}</div>
                <div style={styles.seriesId}>{series.id}</div>
              </div>
            ))}
            {filteredSeries.length === 0 && (
              <div style={styles.noResults}>
                No indicators found. Try a different search term.
              </div>
            )}
          </div>
        </aside>

        <section style={styles.visualizationSection}>
          <div style={styles.visualizationHeader}>
            <h2 style={styles.visualizationTitle}>
              {title || 'Select a dataset to visualize'}
              {units && <span style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '0.5rem' }}>({units})</span>}
              {frequency && (
                <span style={{
                  fontSize: '0.75rem',
                  color: '#fff',
                  backgroundColor: '#3b82f6',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '9999px',
                  marginLeft: '0.75rem',
                  fontWeight: '500',
                }}>
                  {frequency} Data
                </span>
              )}
            </h2>
          </div>

          <div style={styles.controls}>
            <div style={styles.controlGroup}>
              <label htmlFor="chart-type" style={styles.label}>Chart Type</label>
              <select 
                id="chart-type"
                value={chartType} 
                onChange={(e) => setChartType(e.target.value as ChartType)}
                style={styles.select}
              >
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="area">Area Chart</option>
                <option value="composed">Composed Chart</option>
                <option value="pie">Pie Chart</option>
                <option value="scatter">Scatter Plot</option>
                <option value="radar">Radar Chart</option>
              </select>
            </div>
            
            <div style={styles.controlGroup}>
              <label htmlFor="time-range" style={styles.label}>Time Range</label>
              <select 
                id="time-range"
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                style={styles.select}
              >
                <option value="all">All Time</option>
                <option value="30">Last 30 Days</option>
                <option value="90">Last 90 Days</option>
                <option value="180">Last 180 Days</option>
                <option value="365">Last Year</option>
              </select>
            </div>

            <div style={styles.controlGroup}>
              <label style={styles.label}>Options</label>
              <label style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={showMovingAverage}
                  onChange={(e) => setShowMovingAverage(e.target.checked)}
                  style={styles.checkboxInput}
                />
                <span style={styles.label}>Show Moving Average</span>
              </label>
            </div>

            <div style={styles.controlGroup}>
              <label style={styles.label}>Zoom</label>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  onClick={() => {
                    if (!chartData.length) return;
                    const startDate = new Date(chartData[0].date);
                    const endDate = new Date(chartData[chartData.length - 1].date);
                    const range = endDate.getTime() - startDate.getTime();
                    const zoomStart = new Date(endDate.getTime() - (range * 0.1));
                    setZoomDomain({ 
                      start: zoomStart.toISOString().split('T')[0], 
                      end: endDate.toISOString().split('T')[0] 
                    });
                  }}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: '#6366f1',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    minWidth: '90px'
                  }}
                >
                  Last 10%
                </button>
                <button
                  onClick={() => {
                    if (!chartData.length) return;
                    const startDate = new Date(chartData[0].date);
                    const endDate = new Date(chartData[chartData.length - 1].date);
                    const range = endDate.getTime() - startDate.getTime();
                    const zoomStart = new Date(endDate.getTime() - (range * 0.3));
                    setZoomDomain({ 
                      start: zoomStart.toISOString().split('T')[0], 
                      end: endDate.toISOString().split('T')[0] 
                    });
                  }}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    minWidth: '90px'
                  }}
                >
                  Last 30%
                </button>
                <button
                  onClick={() => {
                    if (!chartData.length) return;
                    const startDate = new Date(chartData[0].date);
                    const endDate = new Date(chartData[chartData.length - 1].date);
                    const range = endDate.getTime() - startDate.getTime();
                    const zoomStart = new Date(endDate.getTime() - (range * 0.5));
                    setZoomDomain({ 
                      start: zoomStart.toISOString().split('T')[0], 
                      end: endDate.toISOString().split('T')[0] 
                    });
                  }}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: '#0ea5e9',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    minWidth: '90px'
                  }}
                >
                  Last 50%
                </button>
                {zoomDomain.start && (
                  <button
                    onClick={handleResetZoom}
                    style={{
                      padding: '0.5rem',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      minWidth: '70px'
                    }}
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>
          </div>

          {error ? (
            <div style={{...styles.chartContainer, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{
                ...styles.errorMessage,
                maxWidth: '400px',
                padding: '2rem',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}>
                {error}
              </div>
            </div>
          ) : isLoading ? (
            <div style={{...styles.chartContainer, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '1rem'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  border: '3px solid #f3f4f6',
                  borderTop: '3px solid #3b82f6',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }} />
                <div style={styles.loadingMessage}>Loading data...</div>
              </div>
            </div>
          ) : chartData.length > 0 ? (
            <div style={styles.chartContainer}>
              <ResponsiveContainer width="100%" height="100%">
                {renderChart()}
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{...styles.chartContainer, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={styles.loadingMessage}>
                Search and select a series to display data
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}; 