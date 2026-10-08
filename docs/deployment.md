# Deployment Guide

CryptoMAKA Lab is designed for easy deployment using Docker.

## Local Deployment (Docker Compose)

The easiest way to run the platform locally is using the provided `compose.yaml` file, which uses SQLite for the database.

```bash
docker-compose up --build
```
The application will be available at:
* Frontend: `http://localhost:8080`
* Backend API: `http://localhost:8000/api/v1`

## Production Deployment

For production, it is recommended to use PostgreSQL as the database backend. The `compose.production.yaml` file is configured for this.

1. Copy `.env.example` to `.env` and set secure passwords.
2. Run the production compose file:
```bash
docker-compose -f compose.production.yaml up --build -d
```

## Cloud Deployment (Render)

A `render.yaml` Blueprint is provided in the `deploy/` directory for deploying to Render.com.

1. Connect your GitHub repository to Render.
2. Use the "Blueprint" option and point it to the repository.
3. Render will automatically provision the PostgreSQL database, backend service, and frontend service based on the `render.yaml` configuration.
