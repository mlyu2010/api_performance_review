# Agents & Tasks API

A comprehensive REST API for managing agents, tasks, and task executions with authentication, built with FastAPI and PostgreSQL.

## Dependencies
1. Docker
2. Docker Compose
3. Python 3.12
4. Run scripts/init_db.py to populate the test user 'admin/admin123'

## Features

- FastAPI Framework: Modern, fast Python web framework
- PostgreSQL 18: Robust relational database
- Tortoise ORM: Async ORM for Python
- JWT Authentication: Secure token-based authentication
- Soft Deletion: All deletions are soft deletes (data retained)
- Multi-Agent Tasks: Tasks can support multiple agents
- Task Executions: Run tasks with specific agents
- Rate Limiting: Built-in request rate limiting
- Docker Support: Full Docker and docker-compose setup
- Comprehensive Tests: Unit and integration tests included
- API Documentation and Testing via Web UI: http://localhost:8000/docs
- Performance Testing: via 'k6_load_test' module
- Production and Development Environments: 'docker-compose.yml' and 'docker-compose.prod.yml' files included

## Installation

docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f api

## Documentation

### Generating HTML Documentation

The project includes comprehensive docstrings throughout the codebase. 
You can generate beautiful HTML documentation via 
scripts/generate_docs.py


