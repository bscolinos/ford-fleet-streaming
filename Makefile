# Ford Fleet Management Demo - Makefile
# One-command operations for development and deployment

.PHONY: help setup db-init up down logs clean test loadtest

# Default target
help:
	@echo "Ford Fleet Management Demo - Available Commands"
	@echo ""
	@echo "Setup & Database:"
	@echo "  make setup      - Initial setup (copy .env, build containers)"
	@echo "  make db-init    - Initialize database (schema, security, seed)"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - Tail logs from all services"
	@echo "  make clean      - Stop services and remove volumes"
	@echo ""
	@echo "Development:"
	@echo "  make backend    - Run backend locally (for development)"
	@echo "  make producer   - Run Kafka producer locally"
	@echo "  make consumer   - Run Kafka consumer locally"
	@echo ""
	@echo "Testing:"
	@echo "  make loadtest   - Run load test (10 users, 60s)"
	@echo "  make scaletest  - Run scaling test (1-500 users)"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell      - Open shell in backend container"
	@echo "  make psql       - Connect to SingleStore via mysql client"

# Initial setup
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example - please update with your values"; \
	fi
	docker compose build

# Initialize database
db-init:
	@echo "Initializing database..."
	@echo "Running schema.sql..."
	mysql -h $${SINGLESTORE_HOST:-localhost} -P $${SINGLESTORE_PORT:-3306} \
		-u root -p$${SINGLESTORE_ROOT_PASSWORD:-root} < db/schema.sql
	@echo "Running security.sql..."
	mysql -h $${SINGLESTORE_HOST:-localhost} -P $${SINGLESTORE_PORT:-3306} \
		-u root -p$${SINGLESTORE_ROOT_PASSWORD:-root} < db/security.sql
	@echo "Running seed.sql..."
	mysql -h $${SINGLESTORE_HOST:-localhost} -P $${SINGLESTORE_PORT:-3306} \
		-u root -p$${SINGLESTORE_ROOT_PASSWORD:-root} < db/seed.sql
	@echo "Database initialized!"

# Start all services
up:
	docker compose up -d
	@echo ""
	@echo "Services starting..."
	@echo "  Frontend:  http://localhost:8080"
	@echo "  Backend:   http://localhost:8000/docs"
	@echo "  Redpanda:  http://localhost:8081 (Console)"
	@echo ""

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Clean up everything
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Run backend locally (development)
backend:
	cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run producer locally
producer:
	cd kafka/producer && pip install -r requirements.txt && python telemetry_producer.py

# Run consumer locally
consumer:
	cd kafka/consumer && pip install -r requirements.txt && python telemetry_consumer.py

# Run load test
loadtest:
	cd loadtest && pip install -r requirements.txt && \
		python harness.py --url http://localhost:8000 --users $${USERS:-10} --duration $${DURATION:-60}

# Run scaling test
scaletest:
	cd loadtest && pip install -r requirements.txt && \
		python harness.py --url http://localhost:8000 --scale-test --output results.json

# Open shell in backend container
shell:
	docker compose exec backend /bin/bash

# Connect to SingleStore
psql:
	mysql -h $${SINGLESTORE_HOST:-localhost} -P $${SINGLESTORE_PORT:-3306} \
		-u $${DB_ADMIN_USER:-demo_admin} -p$${DB_ADMIN_PASSWORD:-AdminPass123!} ford_fleet

# Build containers
build:
	docker compose build

# Restart a specific service
restart-%:
	docker compose restart $*

# View logs for a specific service
logs-%:
	docker compose logs -f $*

