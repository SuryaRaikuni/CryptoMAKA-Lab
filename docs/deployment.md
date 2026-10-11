# Deployment Guide

CryptoMAKA Lab is designed for easy deployment using Docker. Both development and production environments are fully containerized.

## 1. Prerequisites

- **Docker Engine** ≥ 24.0
- **Docker Compose** (v2 plugin) – ships with Docker Desktop on Windows.
- **Git** – to clone the repository.
- *(Optional)* **Render CLI** – for cloud deployment.

## 2. Local Development Deployment (Docker Compose)

The `docker/compose.yaml` file runs the full stack using an **SQLite** database for quick iteration.

```bash
# Clone the repo
git clone https://github.com/your-org/cryptomaka.git
cd cryptomaka

# Build and start containers
docker compose -f docker/compose.yaml up --build
```

The services become reachable at:

- Frontend UI: `http://localhost:8080`
- Backend API: `http://localhost:8000/api/v1`

### 2.1 Environment Variables

Create a local `.env` file based on `.env.example`:

```dotenv
# .env (development)
POSTGRES_USER=devuser
POSTGRES_PASSWORD=devpass
POSTGRES_DB=cryptomaka_dev
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# FastAPI secret key (any random 32‑byte string)
FASTAPI_SECRET_KEY=supersecretdevkey

# Enable debug mode
FASTAPI_DEBUG=true
```

> **Note**: The development compose file ignores these variables for the SQLite fallback, but they are kept for consistency with production.

## 3. Production Deployment

For production we use a **PostgreSQL** database and stricter security settings.

```bash
# Copy the example env and set strong secrets
cp .env.example .env.production
# Edit .env.production with secure values
```

Run the production compose:

```bash
docker compose -f docker/compose.production.yaml up --build -d
```

### 3.1 Production Environment Variables

```dotenv
# .env.production
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=<<strong‑password>>
POSTGRES_DB=cryptomaka_prod
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# FastAPI secret key (32‑byte base64)
FASTAPI_SECRET_KEY=<<32‑byte‑base64>>

# Disable debug mode
FASTAPI_DEBUG=false

# Allowed hosts (comma‑separated)
ALLOWED_HOSTS=example.com,api.example.com
```

### 3.2 Database Migrations

The backend uses **SQLAlchemy** with **Alembic** for schema migrations. After containers are up, apply migrations:

```bash
# Exec into the backend container
docker exec -it cryptomaka_backend bash
# Run Alembic upgrade
alembic upgrade head
```

## 4. Cloud Deployment (Render.com)

A `deploy/render.yaml` Blueprint is provided for Render. The steps are:

1. Sign in to Render and create a new **Blueprint**.
2. Connect your GitHub repository.
3. Choose the `render.yaml` file.
4. Render will automatically provision a PostgreSQL instance, build the Docker images, and expose the services.

### 4.1 Render Environment Variables

Configure the following in the Render dashboard (same names as `.env.production`).

## 5. Observability & Logging

- **Backend**: Logs are written to stdout; Docker captures them. Use `docker logs cryptomaka_backend`.
- **Frontend**: Served by Nginx; access logs are available via `docker logs cryptomaka_frontend`.
- **Health Checks**: `GET /health` endpoint returns `200 OK` when the API is ready.

## 6. Security Recommendations

- Rotate `FASTAPI_SECRET_KEY` regularly.
- Use a managed PostgreSQL service with TLS enabled.
- Restrict inbound traffic to ports `80/443` (frontend) and `8000` (backend) behind a reverse proxy or firewall.

---

For a full list of Dockerfiles and compose files, see the `docker/` directory.
