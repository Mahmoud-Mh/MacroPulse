import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useWebSocket } from './WebSocketManager';

export const DataVisualizer = () => {
  const { lastMessage } = useWebSocket();
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    if (lastMessage?.type === 'series_data') {
      const data = lastMessage.data.observations.map((obs: any) => ({
        date: obs.date,
        value: parseFloat(obs.value)
      }));
      setChartData(data);
    }
  }, [lastMessage]);

  return (
    <div className="data-visualizer">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}; 