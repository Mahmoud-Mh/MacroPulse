import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface WebSocketContextType {
  sendMessage: (message: any) => void;
  lastMessage: any;
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider = ({ children }: WebSocketProviderProps) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (!token) return;

    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/economic_data/?token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      // Send initial heartbeat
      ws.send(JSON.stringify({ type: 'heartbeat' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    setSocket(ws);

    // Set up heartbeat interval
    const heartbeatInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000); // Send heartbeat every 30 seconds

    return () => {
      clearInterval(heartbeatInterval);
      ws.close();
    };
  }, [token]);

  const sendMessage = (message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  };

  return (
    <WebSocketContext.Provider value={{ sendMessage, lastMessage, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
}; 