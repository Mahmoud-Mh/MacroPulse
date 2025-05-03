# MacroPulse

MacroPulse is a modern web application for managing and monitoring economic indicators and tasks. It features a React-based frontend with a Django REST API backend, utilizing Celery for task management and Redis for message brokering.

## Features

- **Task Management System**
  - Create, run, and delete tasks
  - Support for manual and scheduled tasks
  - Real-time task status monitoring
  - Task execution history tracking

- **Economic Indicators**
  - Integration with FRED (Federal Reserve Economic Data)
  - Automated data updates
  - Historical data tracking
  - Customizable update schedules

- **Authentication & Security**
  - JWT-based authentication
  - Token refresh mechanism
  - Secure API endpoints
  - Role-based access control

## Technology Stack

### Backend
- Django 5.0.6
- Django REST Framework
- Celery (Task Queue)
- Redis (Message Broker)
- PostgreSQL (Database)
- Flower (Task Monitoring)

### Frontend
- React
- Vite
- React Bootstrap
- date-fns
- Modern UI/UX design

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis Server

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Mahmoud-Mh/MacroPulse.git
   cd MacroPulse
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the root directory:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=macro_pulse
   DB_USER=your-db-user
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432
   FRED_API_KEY=your-fred-api-key
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a .env file in the frontend directory:
   ```
   VITE_API_URL=http://localhost:8000
   ```

## Running the Application

1. Start the Redis server:
   ```bash
   redis-server
   ```

2. Start the Celery worker:
   ```bash
   celery -A macro_pulse worker -l info
   ```

3. Start the Celery beat scheduler:
   ```bash
   celery -A macro_pulse beat -l info
   ```

4. Start the Flower monitoring tool:
   ```bash
   celery -A macro_pulse flower
   ```

5. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

6. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Flower Dashboard: http://localhost:5555

## API Documentation

## Development

### Code Structure

```
macro_pulse/
├── frontend/            # React frontend application
├── macro_pulse/         # Django project settings
├── indicators/          # Economic indicators app
├── authentication/      # Authentication app
├── websocket/          # WebSocket functionality
└── requirements.txt     # Python dependencies
```

### Key Components

- **Task Manager**: Handles task creation, execution, and monitoring
- **Indicator Service**: Manages economic data fetching and updates
- **Authentication System**: Handles user authentication and authorization
- **WebSocket Service**: Provides real-time updates

## Production Deployment

For production deployment:

1. Update environment variables with production values
2. Configure proper web server (e.g., Nginx)
3. Set up SSL/TLS certificates
4. Configure database backups
5. Set up monitoring and logging
6. Configure proper static file serving
