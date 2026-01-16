# Ford Fleet Management Demo

A complete fleet management demo showcasing SingleStore's capabilities for real-time operational analytics, replacing BigQuery while keeping BigTable patterns in place.

## Overview

This demo demonstrates:

- **Transaction Processing** - Point lookups and updates via rowstore tables
- **Fast API Reads** - Sub-millisecond queries against SingleStore
- **Real-time Streaming Ingest** - Kafka topics per customer into shared tables
- **RBAC + RLS Security** - Role-based privileges with row-level visibility
- **Anomaly Detection** - Real-time threshold-based detection
- **AI Integration** - Fleet insights via SingleStore AI proxy (Claude)
- **Load Testing** - Scalable performance harness (1-500+ users)

## Architecture

```
                                    +------------------+
                                    |   SingleStore    |
                                    |     Helios       |
                                    +--------+---------+
                                             |
+-------------+    +-------------+    +------+-------+    +-------------+
|   Redpanda  |--->|   Consumer  |--->|   Rowstore   |<---|   FastAPI   |
|   (Kafka)   |    |   Service   |    |  Columnstore |    |   Backend   |
+------+------+    +-------------+    +--------------+    +------+------+
       ^                                                         |
       |                                                         v
+------+------+                                          +-------+-------+
|   Producer  |                                          |   Dashboard   |
|   Service   |                                          |   (Frontend)  |
+-------------+                                          +---------------+
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- SingleStore Helios workspace (or local SingleStore)
- MySQL client (for database initialization)

### 1. Clone and Configure

```bash
cd ford_demo

# Copy environment template
cp env.example .env

# Edit .env with your SingleStore credentials
vim .env
```

### 2. Initialize Database

Connect to your SingleStore instance and run the SQL scripts:

```bash
# Run schema, security, and seed scripts
mysql -h <SINGLESTORE_HOST> -P 3306 -u root -p < db/schema.sql
mysql -h <SINGLESTORE_HOST> -P 3306 -u root -p < db/security.sql
mysql -h <SINGLESTORE_HOST> -P 3306 -u root -p < db/seed.sql
```

### 3. Start Services

```bash
# Build and start all containers
docker compose up -d

# View logs
docker compose logs -f
```

### 4. Access the Demo

- **Dashboard**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **Redpanda Console**: http://localhost:8081

## Local Development (without Docker)

For development without Docker, you can run the frontend and backend separately:

### 1. Setup Python Environment

```bash
cd ford_demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your SingleStore credentials
```

### 3. Start Backend

```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 4. Start Frontend (separate terminal)

```bash
cd frontend
python3 -m http.server 8000
```

### 5. Access the Demo

- **Dashboard**: http://localhost:8000
- **API**: http://localhost:8080/docs

Note: For streaming data, you'll need either:
- EC2 streaming setup (see `ec2-streaming/README.md`)
- Or run Docker Compose for local Kafka: `docker compose up redpanda producer consumer`

### Demo Credentials

| Username | Password | Role | Scope |
|----------|----------|------|-------|
| `territory_manager_1` | `territory123` | Territory Manager | WEST_1 territory only |
| `regional_manager_1` | `regional123` | Regional Manager | All WEST territories |
| `demo_admin` | `admin123` | Admin | Full access |

## Project Structure

```
ford_demo/
├── db/
│   ├── schema.sql          # Table definitions
│   ├── security.sql        # RBAC roles, users, RLS views
│   └── seed.sql            # Demo data
├── kafka/
│   ├── producer/           # Telemetry event generator
│   └── consumer/           # SingleStore ingestor
├── backend/
│   └── app/
│       ├── auth/           # JWT authentication
│       ├── fleet/          # Fleet API endpoints
│       ├── realtime/       # WebSocket handler
│       └── ai/             # AI integration
├── frontend/
│   ├── index.html          # Dashboard HTML
│   ├── css/styles.css      # Styling
│   └── js/                 # JavaScript modules
├── loadtest/
│   ├── harness.py          # Load testing harness
│   └── scenarios.py        # Test scenarios
├── aws/
│   ├── msk-config.json     # MSK configuration
│   ├── ecs-task-def.json   # ECS task definitions
│   └── deploy.sh           # Deployment script
├── docker-compose.yml      # Local development
├── Makefile                # Convenience commands
└── README.md
```

## Database Schema

### Rowstore Tables (Transactional)

| Table | Purpose |
|-------|---------|
| `customers` | Customer metadata with Kafka topic names |
| `users` | Application users with role assignments |
| `vehicles` | Fleet vehicles with region/territory mapping |
| `vehicle_state` | Latest vehicle status (upsert target) |
| `anomalies` | Detected anomalies with acknowledgement state |

### Columnstore Tables (Analytics)

| Table | Purpose |
|-------|---------|
| `telemetry_raw` | All telemetry events from Kafka |
| `driver_notes` | Free-text notes for AI summarization |

### RLS Views

All sensitive tables have corresponding RLS views (`v_telemetry_raw`, `v_vehicles`, etc.) that filter rows using `SECURITY_LISTS_INTERSECT()`.

## Security Model

### Database Roles

- `fleet_territory_manager` - Territory-scoped read access
- `fleet_regional_manager` - Region-scoped read access
- `fleet_admin` - Full read access
- `fleet_ingest` - Insert-only for Kafka consumer

### Security Roles (for RLS)

- `territory_west_1`, `territory_west_2`, etc. - Per-territory access
- `region_west`, `region_east`, `region_central` - Per-region access
- `admin_all` - Sees all data

### ACCESS_ROLES Column

Each row contains an `access_roles` column formatted as `,ROLE_A,ROLE_B,`:

```sql
-- Example: visible to WEST_1 territory and all WEST regional managers
access_roles = ',territory_west_1,region_west,admin_all,'
```

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Authenticate, returns JWT |
| `/auth/me` | GET | Current user info |

### Fleet Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/fleet/summary` | GET | Aggregated KPIs + timeseries |
| `/fleet/vehicles` | GET | Vehicle list with filters |
| `/fleet/vehicle/{id}/telemetry` | GET | Vehicle telemetry history |
| `/fleet/anomalies` | GET | Anomaly list with filters |
| `/fleet/anomalies/{id}/ack` | POST | Acknowledge anomaly |
| `/fleet/notes` | GET | Driver notes |

### AI

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/summarize` | POST | Summarize driver notes |
| `/ai/insights` | POST | Fleet insights Q&A |

### Real-time

| Endpoint | Type | Description |
|----------|------|-------------|
| `/realtime/stream` | WebSocket | Dashboard updates every 2s |

## Load Testing

### Quick Test

```bash
# 10 users for 60 seconds
make loadtest USERS=10 DURATION=60
```

### Scaling Test

```bash
# Test 1, 100, 200, 500 concurrent users
make scaletest
```

### Custom Test

```bash
cd loadtest
python harness.py --url http://localhost:8000 --users 200 --duration 120
```

### Expected Results

| Users | Throughput | p50 Latency | p95 Latency |
|-------|------------|-------------|-------------|
| 1 | 10 req/s | 15ms | 25ms |
| 100 | 500 req/s | 45ms | 120ms |
| 200 | 800 req/s | 65ms | 180ms |
| 500 | 1200 req/s | 95ms | 280ms |

*Results vary based on SingleStore configuration and network latency.*

## Demo Narrative

### 1. Login as Territory Manager

Show how `territory_manager_1` only sees WEST_1 territory data:
- Limited vehicle count
- Filtered telemetry
- Only WEST_1 anomalies

### 2. Real-time Telemetry

Watch the dashboard update as Kafka events flow in:
- KPI cards updating
- Charts animating
- Map markers moving

### 3. Anomaly Detection

Demonstrate real-time anomaly detection:
- High engine temp alerts
- Low battery warnings
- DTC code detection

### 4. Acknowledge Anomaly

Show transactional write capability:
- Click ACK button
- Verify immediate update
- Demonstrate rowstore transaction

### 5. Switch to Regional Manager

Login as `regional_manager_1` to show RLS in action:
- Now sees all WEST territories
- More vehicles visible
- Broader anomaly scope

### 6. AI Insights

Use the AI panel to ask fleet questions:
- "What are the top issues in my fleet?"
- "Summarize driver notes"
- "How is fuel efficiency trending?"

### 7. Load Test Results

Show performance at scale:
- Run quick load test
- Display latency percentiles
- Discuss production scaling path

## AWS Deployment

### Components

- **MSK** - Managed Kafka cluster
- **ECS Fargate** - Container hosting
- **ALB** - Load balancing
- **ECR** - Container registry
- **Secrets Manager** - Credentials storage

### Deploy

```bash
# Configure AWS CLI
aws configure

# Run deployment
cd aws
./deploy.sh
```

See `aws/` directory for configuration templates.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SINGLESTORE_HOST` | Database host | `localhost` |
| `SINGLESTORE_PORT` | Database port | `3306` |
| `SINGLESTORE_DATABASE` | Database name | `ford_fleet` |
| `JWT_SECRET_KEY` | JWT signing key | (required) |
| `MODEL_API_AUTH` | SingleStore AI key | (optional) |
| `EVENTS_PER_SECOND` | Producer rate | `10` |
| `ANOMALY_PROBABILITY` | Anomaly frequency | `0.02` |

### Tuning

For production workloads:

1. **Connection Pooling** - Increase pool sizes in backend
2. **Batch Size** - Adjust consumer batch size (100-1000)
3. **Partitions** - Add Kafka partitions for parallelism
4. **Replicas** - Scale ECS tasks horizontally

## Troubleshooting

### Database Connection Failed

1. Verify `SINGLESTORE_HOST` is accessible
2. Check firewall/security group rules
3. Confirm user credentials in `security.sql`

### Kafka Consumer Not Ingesting

1. Check Redpanda Console for topic messages
2. Verify consumer logs: `docker compose logs consumer`
3. Confirm database permissions for `ingest_user`

### RLS Not Filtering

1. Verify `ACCESS_ROLES` column format: `,role_name,`
2. Check security role grants in `security.sql`
3. Test with: `SELECT CURRENT_SECURITY_ROLES();`

### AI Not Responding

1. Verify `MODEL_API_AUTH` is set
2. Check network connectivity to AI endpoint
3. Review backend logs for error details

## License

MIT License - See LICENSE file for details.

## Support

For questions about this demo, contact your SingleStore representative.

