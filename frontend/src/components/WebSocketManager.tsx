import { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';

interface WebSocketContextType {
  sendMessage: (message: any) => void;
  lastMessage: any;
  isConnected: boolean;
  isReconnecting: boolean;
  error: string | null;
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
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const token = localStorage.getItem('access_token');
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatInterval = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    if (!token) return;
    setError(null);
    setIsReconnecting(reconnectAttempts.current > 0);
    const wsInstance = new WebSocket(`ws://127.0.0.1:8000/ws/economic_data/?token=${token}`);
    wsRef.current = wsInstance;

    wsInstance.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      setIsReconnecting(false);
      reconnectAttempts.current = 0;
      setError(null);
      wsInstance.send(JSON.stringify({ type: 'heartbeat' }));
    };

    wsInstance.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (error) {
        setError('Error parsing WebSocket message');
        console.error('Error parsing WebSocket message:', error);
      }
    };

    wsInstance.onclose = () => {
      setIsConnected(false);
      setIsReconnecting(true);
      setError('WebSocket disconnected. Attempting to reconnect...');
      if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
      const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);
      reconnectTimeout.current = setTimeout(() => {
        reconnectAttempts.current += 1;
        connect();
      }, delay);
    };

    wsInstance.onerror = () => {
      setError('WebSocket error.');
      setIsConnected(false);
      setIsReconnecting(true);
      wsInstance.close();
    };

    heartbeatInterval.current = setInterval(() => {
      if (wsInstance.readyState === WebSocket.OPEN) {
        wsInstance.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);
  };

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
      if (wsRef.current) wsRef.current.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setError('WebSocket is not connected');
      console.error('WebSocket is not connected');
    }
  };

  return (
    <WebSocketContext.Provider value={{ sendMessage, lastMessage, isConnected, isReconnecting, error }}>
      {children}
    </WebSocketContext.Provider>
  );
}; 