import React, { useEffect, useState } from 'react';
import Card from 'react-bootstrap/Card';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import { Navigate, Link, useLocation } from 'react-router-dom';
import { format, parseISO } from 'date-fns';

interface Task {
  id: number;
  name: string;
  status: string;
  last_run: string;
}

const styles = {
  root: {
    margin: 0,
    padding: 0,
    width: '100vw',
    height: '100vh',
    overflow: 'hidden',
    backgroundColor: '#f3f4f6',
  },
  nav: {
    backgroundColor: '#f8f9fa',
    padding: '10px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  navLinks: {
    display: 'flex',
    gap: '20px',
  },
  navLink: {
    textDecoration: 'none',
    color: '#333',
    padding: '8px 16px',
    borderRadius: '4px',
    transition: 'all 0.3s ease',
  },
  navLinkActive: {
    backgroundColor: '#e9ecef',
    color: '#007bff',
  },
  content: {
    padding: '2rem',
    height: 'calc(100vh - 60px)',
    overflow: 'auto',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '1rem',
    boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
    border: 'none',
    marginBottom: '2rem',
  },
  header: {
    backgroundColor: '#6366f1',
    color: 'white',
    padding: '1.5rem',
    borderRadius: '1rem 1rem 0 0',
    border: 'none',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 600,
    margin: 0,
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    padding: '1.5rem',
  },
  formRow: {
    display: 'flex',
    gap: '1rem',
  },
  formGroup: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  label: {
    color: '#1e293b',
    fontWeight: 500,
    fontSize: '0.875rem',
  },
  input: {
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #e2e8f0',
    fontSize: '0.875rem',
    backgroundColor: '#f8fafc',
    color: '#1e293b',
    outline: 'none',
    transition: 'border 0.2s',
    '&:focus': {
      borderColor: '#6366f1',
      boxShadow: '0 0 0 1px #6366f1',
    },
  },
  select: {
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #e2e8f0',
    fontSize: '0.875rem',
    backgroundColor: '#f8fafc',
    color: '#1e293b',
    outline: 'none',
    transition: 'border 0.2s',
    '&:focus': {
      borderColor: '#6366f1',
      boxShadow: '0 0 0 1px #6366f1',
    },
  },
  buttonCreate: {
    backgroundColor: '#6366f1',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '0.5rem',
    fontWeight: 500,
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'background 0.2s',
    '&:hover': {
      backgroundColor: '#4f46e5',
    },
  },
  table: {
    margin: 0,
  },
  tableHeader: {
    backgroundColor: '#f8fafc',
    color: '#1e293b',
    fontWeight: 600,
    borderBottom: '2px solid #e2e8f0',
  },
  tableCell: {
    color: '#1e293b',
    padding: '1rem',
    verticalAlign: 'middle',
  },
  statusActive: {
    color: '#059669',
    fontWeight: 500,
  },
  statusInactive: {
    color: '#dc2626',
    fontWeight: 500,
  },
  buttonRun: {
    backgroundColor: '#6366f1',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontWeight: 500,
    '&:hover': {
      backgroundColor: '#4f46e5',
    },
  },
  buttonDelete: {
    backgroundColor: '#ef4444',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontWeight: 500,
    '&:hover': {
      backgroundColor: '#dc2626',
    },
  },
};

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link 
      to={to} 
      style={{
        ...styles.navLink,
        ...(isActive ? styles.navLinkActive : {})
      }}
    >
      {children}
    </Link>
  );
}

const TaskManager: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTask, setNewTask] = useState({
    name: '',
    status: 'Active',
    schedule: 'manual',
  });
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const token = localStorage.getItem('access_token');

  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/indicators/tasks/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      if (response.status === 401) {
        // Token expired, try to refresh
        try {
          const refreshResponse = await fetch(`${API_URL}/api/v1/auth/token/refresh/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh: localStorage.getItem('refresh_token'),
            }),
            credentials: 'include',
          });

          if (!refreshResponse.ok) {
            throw new Error('Token refresh failed');
          }

          const { access } = await refreshResponse.json();
          localStorage.setItem('access_token', access);

          // Retry the original request with new token
          const retryResponse = await fetch(`${API_URL}/api/v1/indicators/tasks/`, {
            headers: {
              'Authorization': `Bearer ${access}`,
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });

          if (!retryResponse.ok) {
            throw new Error('Failed to fetch tasks after token refresh');
          }

          const data = await retryResponse.json();
          setTasks(data);
          return;
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return;
        }
      }

      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }

      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/api/v1/indicators/tasks/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newTask),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to create task' }));
        throw new Error(errorData.error || 'Failed to create task');
      }

      const createdTask = await response.json();
      setTasks([...tasks, createdTask]);
      setNewTask({ name: '', status: 'Active', schedule: 'manual' });
    } catch (error) {
      console.error('Error creating task:', error);
      alert(error instanceof Error ? error.message : 'Failed to create task');
    }
  };

  const handleRunTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/indicators/tasks/${taskId}/run/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (response.status === 401) {
        // Token expired, try to refresh
        try {
          const refreshResponse = await fetch(`${API_URL}/api/v1/auth/token/refresh/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh: localStorage.getItem('refresh_token'),
            }),
            credentials: 'include',
          });

          if (!refreshResponse.ok) {
            throw new Error('Token refresh failed');
          }

          const { access } = await refreshResponse.json();
          localStorage.setItem('access_token', access);

          // Retry the run request with new token
          const retryResponse = await fetch(`${API_URL}/api/v1/indicators/tasks/${taskId}/run/`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${access}`,
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });

          if (!retryResponse.ok) {
            throw new Error('Failed to run task after token refresh');
          }

          const result = await retryResponse.json();
          console.log('Task execution started:', result);
          
          // Update the task's last run time in the local state
          if (result.last_run) {
            setTasks(prevTasks => prevTasks.map(task => 
              task.id === taskId 
                ? { ...task, last_run: result.last_run } 
                : task
            ));
          }

          // Poll for task completion and update last run time
          const pollInterval = setInterval(async () => {
            try {
              const taskResponse = await fetch(`${API_URL}/api/v1/indicators/tasks/`, {
                headers: {
                  'Authorization': `Bearer ${access}`,
                  'Content-Type': 'application/json',
                },
                credentials: 'include',
              });
              
              if (taskResponse.ok) {
                const tasks = await taskResponse.json();
                const updatedTask = tasks.find((t: Task) => t.id === taskId);
                if (updatedTask && updatedTask.last_run) {
                  setTasks(prevTasks => prevTasks.map(task => 
                    task.id === taskId ? updatedTask : task
                  ));
                  clearInterval(pollInterval);
                }
              }
            } catch (error) {
              console.error('Error polling task status:', error);
              clearInterval(pollInterval);
            }
          }, 2000); // Poll every 2 seconds

          // Clear polling after 30 seconds to prevent infinite polling
          setTimeout(() => clearInterval(pollInterval), 30000);
          
          return;
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return;
        }
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to run task');
      }

      const result = await response.json();
      console.log('Task execution started:', result);
      
      // Update the task's last run time in the local state
      if (result.last_run) {
        setTasks(prevTasks => prevTasks.map(task => 
          task.id === taskId 
            ? { ...task, last_run: result.last_run } 
            : task
        ));
      }

      // Poll for task completion and update last run time
      const pollInterval = setInterval(async () => {
        try {
          const taskResponse = await fetch(`${API_URL}/api/v1/indicators/tasks/`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });
          
          if (taskResponse.ok) {
            const tasks = await taskResponse.json();
            const updatedTask = tasks.find((t: Task) => t.id === taskId);
            if (updatedTask && updatedTask.last_run) {
              setTasks(prevTasks => prevTasks.map(task => 
                task.id === taskId ? updatedTask : task
              ));
              clearInterval(pollInterval);
            }
          }
        } catch (error) {
          console.error('Error polling task status:', error);
          clearInterval(pollInterval);
        }
      }, 2000); // Poll every 2 seconds

      // Clear polling after 30 seconds to prevent infinite polling
      setTimeout(() => clearInterval(pollInterval), 30000);
      
    } catch (error) {
      console.error('Error running task:', error);
      alert(error instanceof Error ? error.message : 'Failed to run task');
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/indicators/tasks/${taskId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (response.status === 401) {
        // Token expired, try to refresh
        try {
          const refreshResponse = await fetch(`${API_URL}/api/v1/auth/token/refresh/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh: localStorage.getItem('refresh_token'),
            }),
            credentials: 'include',
          });

          if (!refreshResponse.ok) {
            throw new Error('Token refresh failed');
          }

          const { access } = await refreshResponse.json();
          localStorage.setItem('access_token', access);

          // Retry the delete request with new token
          const retryResponse = await fetch(`${API_URL}/api/v1/indicators/tasks/${taskId}/`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${access}`,
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });

          if (!retryResponse.ok) {
            throw new Error('Failed to delete task after token refresh');
          }

          // Remove the task from the local state
          setTasks(tasks.filter(task => task.id !== taskId));
          return;
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return;
        }
      }

      // Handle 204 No Content and other successful responses
      if (response.ok) {
        // Remove the task from the local state
        setTasks(tasks.filter(task => task.id !== taskId));
        return;
      }

      if (response.status === 204) {
        // No content response, task was deleted successfully
        setTasks(tasks.filter(task => task.id !== taskId));
        return;
      }

      // For other non-successful responses, try to parse the error
      let errorText = '';
      try {
        // Try parsing as JSON first
        const errorData = await response.json();
        errorText = errorData.error || errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        // If not JSON, get as text
        errorText = await response.text() || `Error: HTTP ${response.status}`;
      }

      throw new Error(errorText);
    } catch (error) {
      console.error('Error deleting task:', error);
      alert(error instanceof Error ? error.message : 'Failed to delete task');
    }
  };

  const formatLastRun = (lastRun: string | null) => {
    if (!lastRun) return 'Never';
    try {
      const date = parseISO(lastRun);
      return format(date, 'yyyy-MM-dd HH:mm:ss');
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Never';
    }
  };

  if (!token) {
    return <Navigate to="/login" />;
  }

  return (
    <div style={styles.root}>
      <nav style={styles.nav}>
        <div style={styles.navLinks}>
          <NavLink to="/dashboard">Data Visualizer</NavLink>
          <NavLink to="/monitoring">System Status</NavLink>
          <NavLink to="/task-manager">Task Manager</NavLink>
        </div>
      </nav>
      <div style={styles.content}>
        <Card style={styles.card}>
          <Card.Header style={styles.header}>
            <h3 style={styles.title}>Create New Task</h3>
          </Card.Header>
          <Card.Body>
            <form onSubmit={handleCreateTask} style={styles.form}>
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Task Name</label>
                  <input
                    type="text"
                    value={newTask.name}
                    onChange={(e) => setNewTask({...newTask, name: e.target.value})}
                    style={styles.input}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Status</label>
                  <select
                    value={newTask.status}
                    onChange={(e) => setNewTask({...newTask, status: e.target.value})}
                    style={styles.select}
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Schedule</label>
                  <select
                    value={newTask.schedule}
                    onChange={(e) => setNewTask({...newTask, schedule: e.target.value})}
                    style={styles.select}
                  >
                    <option value="manual">Manual</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
              </div>
              <Button type="submit" style={styles.buttonCreate}>
                Create Task
              </Button>
            </form>
          </Card.Body>
        </Card>

        <Card style={styles.card}>
          <Card.Header style={styles.header}>
            <h3 style={styles.title}>Task Manager</h3>
          </Card.Header>
          <Card.Body>
            <Table style={styles.table} hover>
              <thead>
                <tr>
                  <th style={styles.tableHeader}>Task Name</th>
                  <th style={styles.tableHeader}>Status</th>
                  <th style={styles.tableHeader}>Last Run</th>
                  <th style={styles.tableHeader}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(task => (
                  <tr key={task.id}>
                    <td style={styles.tableCell}>{task.name}</td>
                    <td style={{...styles.tableCell, ...(task.status === 'Active' ? styles.statusActive : styles.statusInactive)}}>
                      {task.status}
                    </td>
                    <td style={styles.tableCell}>
                      {formatLastRun(task.last_run)}
                    </td>
                    <td style={styles.tableCell}>
                      <Button 
                        style={styles.buttonRun} 
                        size="sm" 
                        className="me-2"
                        onClick={() => handleRunTask(task.id)}
                      >
                        Run
                      </Button>
                      <Button 
                        style={styles.buttonDelete} 
                        size="sm"
                        onClick={() => handleDeleteTask(task.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default TaskManager; 