# Architecture Overview

CryptoMAKA Lab is structured as a modern monorepo containing a Python FastAPI backend and a React/Vite frontend.

```mermaid
flowchart TD
    subgraph Backend
        A[API Layer] --> B[Protocol Service]
        B --> C[Ju-Park Protocol]
        B --> D[ECC Protocol]
        B --> E[Reduced Roundtrip]
        A --> F[Security Service]
        A --> G[Benchmark Service]
        A --> H[Experiment Service]
        G --> I[Metrics Collector]
        H --> J[Database (PostgreSQL)]
    end
    subgraph Frontend
        K[React SPA] --> L[Router]
        L --> M[ProtocolSimulator]
        L --> N[SecurityLab]
        L --> O[BenchmarkLab]
        L --> P[ExperimentHistory]
        M --> Q[ProtocolFlow Component]
    end
    Backend -->|REST API| Frontend
    subgraph Deployment
        R[Docker Compose] --> Backend
        R --> Frontend
        R --> DB[PostgreSQL]
    end
```

## Backend Architecture

The backend is organized into domain‑specific modules under `backend/cryptomaka/`:

- **`protocols/`**: Implementations of the cryptographic protocols.
  - `ju_park.py`: Normalized Ju‑Park 2023 protocol.
  - `ecc.py`: ECC/ECDH counterpart using NIST P‑256.
  - `reduced_roundtrip.py`: Proposed 3‑message extension.
- **`security/`**: Automated attack simulations (`runner.py`).
- **`benchmarks/`**: Execution and metric collection for protocol performance (`runner.py`, `metrics.py`, `communication.py`).
- **`quantum/`**: Conceptual quantum threat analysis module.
- **`api/`**: FastAPI route handlers for different domain features.
- **`database/`**: SQLAlchemy models and session management for data persistence (SQLite for dev, PostgreSQL for prod).
- **`schemas/`**: Pydantic models for API request/response validation.

## Frontend Architecture

The frontend is a Single Page Application (SPA) built with React, TypeScript, and Vite.

- **Routing**: `react-router-dom` handles navigation between the different "Labs" (Simulator, Security, Benchmark, Quantum).
- **Styling**: Tailwind CSS for utility‑first styling.
- **Charting**: Recharts for visualizing benchmark metrics.
- **State/API**: A custom API service (`services/api.ts`) interacts with the backend.

## Deployment

The application is containerized using multi‑stage Docker builds:

- `backend.Dockerfile`: Builds the Python environment and runs the FastAPI app.
- `frontend.Dockerfile`: Builds the React app and serves it using Nginx (with API proxying).
- `compose.yaml`: Local orchestration.
- `compose.production.yaml`: Production orchestration including a PostgreSQL database container.

The above diagram and description provide a high‑level view of the system components and their interactions.
