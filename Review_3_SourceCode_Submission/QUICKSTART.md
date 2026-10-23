# Quick Start Guide — CryptoMAKA Lab

This guide helps you set up, run, and experiment with the CryptoMAKA Lab platform in less than 5 minutes.

---

## Prerequisites

- **Python**: 3.11 or 3.12+
- **Node.js**: v18+ or v20+ (with npm)
- **Git**
- *(Optional)* **Docker & Docker Compose** for containerized full-stack deployment.

---

## 1. Local Development (Backend + Frontend)

### Backend (FastAPI)

1. Navigate to the project root and create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     source .venv/bin/activate
     ```

3. Install editable package and development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run the API server:
   ```bash
   uvicorn cryptomaka.main:app --reload --host 127.0.0.1 --port 8000
   ```
   - Interactive Swagger API docs: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

### Frontend (React + Vite + Tailwind CSS)

1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open your browser at `http://localhost:5173`.

---

## 2. Full-Stack Docker Deployment (Production Mode)

To launch the backend, frontend SPA, and PostgreSQL database with a single command:

```bash
docker compose -f docker/compose.yaml up --build -d
```

- Web Dashboard: `http://localhost:8080`
- API / Docs: `http://localhost:8080/docs`
- Stop services: `docker compose -f docker/compose.yaml down`

---

## 3. Running Automated Tests & Linting

Run tests across all protocol implementations and security attack vectors:

```bash
# Unit & integration tests
pytest tests/ -v

# Code style & linting
ruff check .

# Security scan
bandit -r backend/cryptomaka
```

---

## 4. Key Experiments & Features to Explore

1. **Protocol Flow Sequence**: Visualize 3-party mutual authentication (User ↔ Cloud Server ↔ IoT Device) with step-by-step cryptographic transformations.
2. **Security Lab**: Run automated attack simulations (replay, timestamp alteration, message tampering, and impersonation).
3. **Benchmark Lab**: Execute microsecond-precision benchmarks (`perf_counter_ns`) comparing Ju-Park 2023, ECC/ECDH P-256 baseline, and Reduced-Roundtrip extension.
4. **Quantum Threat Analysis**: Review post-quantum vulnerability analysis (Shor vs. Grover) and FIPS 203/204 transition roadmaps.
5. **Experiment History**: Export structured test results in CSV or JSON.
