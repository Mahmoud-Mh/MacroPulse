import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faTasks, 
  faServer, 
  faDatabase, 
  faMemory 
} from '@fortawesome/free-solid-svg-icons';
import './MonitoringDashboard.css';

interface ServiceStatus {
  connected: boolean;
  error?: string;
}

const MonitoringDashboard: React.FC = () => {
  const [status, setStatus] = useState<{
    celery: ServiceStatus;
    rabbitmq: ServiceStatus;
    database: ServiceStatus;
    redis: ServiceStatus;
  }>({
    celery: { connected: false },
    rabbitmq: { connected: false },
    database: { connected: false },
    redis: { connected: false },
  });

  const checkStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/health/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const health = response.data;

      setStatus({
        celery: { 
          connected: health.celery === 'ok',
          error: health.celery !== 'ok' ? health.celery : undefined
        },
        rabbitmq: { 
          connected: health.rabbitmq === 'ok',
          error: health.rabbitmq !== 'ok' ? health.rabbitmq : undefined
        },
        database: { 
          connected: health.database === 'ok',
          error: health.database !== 'ok' ? health.database : undefined
        },
        redis: { 
          connected: health.redis === 'ok',
          error: health.redis !== 'ok' ? health.redis : undefined
        },
      });
    } catch (error: any) {
      console.error('Error checking status:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to check status';
      setStatus({
        celery: { connected: false, error: errorMessage },
        rabbitmq: { connected: false, error: errorMessage },
        database: { connected: false, error: errorMessage },
        redis: { connected: false, error: errorMessage },
      });
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const StatusCard: React.FC<{
    title: string;
    icon: any;
    status: ServiceStatus;
  }> = ({ title, icon, status }) => (
    <div className={`status-card ${status.connected ? 'connected' : 'disconnected'}`}>
      <div className="status-icon">
        <FontAwesomeIcon icon={icon} />
      </div>
      <div className="status-content">
        <h3>{title}</h3>
        <p>{status.connected ? 'Connected' : 'Disconnected'}</p>
        {status.error && <p className="error-message">{status.error}</p>}
      </div>
    </div>
  );

  return (
    <div className="monitoring-dashboard">
      <h2>System Status</h2>
      <div className="status-grid">
        <StatusCard
          title="Celery"
          icon={faTasks}
          status={status.celery}
        />
        <StatusCard
          title="RabbitMQ"
          icon={faServer}
          status={status.rabbitmq}
        />
        <StatusCard
          title="Database"
          icon={faDatabase}
          status={status.database}
        />
        <StatusCard
          title="Redis"
          icon={faMemory}
          status={status.redis}
        />
      </div>
    </div>
  );
};

export default MonitoringDashboard; 