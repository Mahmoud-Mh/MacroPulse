import { getAccessToken } from './auth';

type WebSocketEvent = 'open' | 'close' | 'error' | 'message';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // 1 second
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private eventHandlers: Map<WebSocketEvent, ((data: any) => void)[]> = new Map();
  private connectionUrl: string;

  constructor(url: string) {
    this.connectionUrl = url;
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    const token = getAccessToken();
    if (!token) {
      console.error('No access token available for WebSocket connection');
      return;
    }

    // Create WebSocket with token in URL
    const url = new URL(this.connectionUrl);
    url.searchParams.set('token', token);
    this.socket = new WebSocket(url.toString());
    
    // Set up event handlers
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Trigger open event handlers
      this.triggerEvent('open', {});
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Trigger message event handlers
        this.triggerEvent('message', data);
        
        // Also trigger type-specific handlers
        const handlers = this.messageHandlers.get(data.type);
        if (handlers) {
          handlers.forEach(handler => handler(data));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.socket = null;
      
      // Trigger close event handlers
      this.triggerEvent('close', event);
      
      // Handle specific close codes
      switch (event.code) {
        case 4001:
          console.error('Authentication failed: No token provided');
          break;
        case 4002:
          console.error('Authentication failed: Invalid or expired token');
          break;
        case 4003:
          console.error('Authentication failed: Authentication error');
          break;
        case 1011:
          console.error('Server error:', event.reason);
          break;
        default:
          // Attempt to reconnect if not explicitly closed
          if (event.code !== 1000) {
            this.attemptReconnect();
          }
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.triggerEvent('error', error);
    };
  }

  private triggerEvent(event: WebSocketEvent, data: any) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1));
  }

  disconnect() {
    if (this.socket) {
      this.socket.close(1000, 'Client disconnecting');
      this.socket = null;
    }
  }

  send(data: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  on(event: WebSocketEvent | string, handler: (data: any) => void) {
    if (['open', 'close', 'error', 'message'].includes(event)) {
      if (!this.eventHandlers.has(event as WebSocketEvent)) {
        this.eventHandlers.set(event as WebSocketEvent, []);
      }
      this.eventHandlers.get(event as WebSocketEvent)?.push(handler);
    } else {
      if (!this.messageHandlers.has(event)) {
        this.messageHandlers.set(event, []);
      }
      this.messageHandlers.get(event)?.push(handler);
    }
  }

  off(event: WebSocketEvent | string, handler: (data: any) => void) {
    if (['open', 'close', 'error', 'message'].includes(event)) {
      const handlers = this.eventHandlers.get(event as WebSocketEvent);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    } else {
      const handlers = this.messageHandlers.get(event);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    }
  }
}

// Create instances for different WebSocket endpoints
export const economicDataSocket = new WebSocketService('ws://127.0.0.1:8000/ws/economic_data/');
export const indicatorsSocket = new WebSocketService('ws://127.0.0.1:8000/ws/indicators/'); 