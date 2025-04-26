# MacroPulse

A real-time macroeconomic indicators pipeline for quantitative analysis and trading decisions.

## Overview

MacroPulse is a robust platform that collects, stores, analyzes, and visualizes macroeconomic indicators (interest rates, inflation, PMI, etc.) to generate decision-making signals. It provides real-time access to reliable macro indicators for quantitative and IT teams.

### Key Features

- REST API for querying and historizing indicators
- Automated update tasks via Celery workers
- Real-time WebSocket dashboard for live monitoring
- Partitioned PostgreSQL database for efficient data storage
- Docker-based deployment for easy scaling

## Architecture

The project uses a modern tech stack:

- **Backend**: Django 4+ with Django REST Framework
- **Database**: PostgreSQL 14+ with partitioning
- **Task Queue**: Celery 5 with RabbitMQ
- **Data Source**: FRED (Federal Reserve Economic Data) API
- **Real-time**: Django Channels with WebSocket
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Flower for Celery monitoring

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 14+
- RabbitMQ
- Docker & Docker Compose
- FRED API Key (get it from https://fred.stlouisfed.org/docs/api/api_key.html)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/macro-pulse.git
cd macro-pulse
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp setup.example.env .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start development server:
```bash
python manage.py runserver
```

### Docker Deployment

1. Build and start services:
```bash
docker-compose up --build
```

2. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

## API Documentation

API documentation is available at `/api/docs/` (Swagger UI) when the server is running.

### Main Endpoints

- `GET /api/indicators/`: List all indicators
- `GET /api/indicators/{id}/`: Get specific indicator details
- `GET /api/indicators/{series_id}/history/`: Get historical data for an indicator
- `GET /api/indicators/search/?q={query}`: Search indicators
- `GET /api/indicators/categories/`: List FRED data categories

## Monitoring

- Celery task monitoring: Access Flower at `http://localhost:5555`
- Task queue monitoring via RabbitMQ Management UI at `http://localhost:15672`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 