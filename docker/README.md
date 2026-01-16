# Docker Configuration

## Purpose
Contains Docker configurations for containerizing all services, enabling consistent development and production environments.

## Structure
```
docker/
├── frontend/
│   └── Dockerfile               # Frontend container
├── backend/
│   └── Dockerfile               # Backend API container
├── ai-modules/
│   ├── Dockerfile.stt           # Speech-to-Text container
│   ├── Dockerfile.nlp           # NLP Evaluation container
│   ├── Dockerfile.qgen          # Question Generation container
│   └── Dockerfile.scoring       # Scoring Engine container
├── database/
│   └── Dockerfile               # Database container
├── nginx/
│   ├── Dockerfile               # Nginx reverse proxy
│   └── nginx.conf               # Nginx configuration
├── docker-compose.yml           # Development compose
├── docker-compose.prod.yml      # Production compose
└── .env.example                 # Environment variables template
```

## Quick Start
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up backend -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```
