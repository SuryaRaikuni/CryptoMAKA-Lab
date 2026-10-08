# CryptoMAKA Lab

A web-based experimental platform for cloud-IoT mutual authentication and key-agreement research.

This repository transforms the existing Crypto MAKA research prototype into a complete, reproducible, and deployable cybersecurity research platform.

## Features

1. **Protocol Implementations**:
   - Faithful normalized implementation of the Ju-Park 2023 lightweight MAKA protocol.
   - ECC/ECDH counterpart using modern cryptographic primitives (NIST P-256).
   - Proposed reduced-round-trip extension (3-message optimization).
2. **Security Lab**: Automated attack simulations (replay, tampering, impersonation).
3. **Benchmark Lab**: Reproducible computation and communication benchmarks.
4. **Quantum Threat Analysis**: Conceptual analysis of post-quantum security implications.
5. **Web Dashboard**: Interactive UI for running experiments and visualizing results.
6. **Deployment Ready**: Production-style Docker deployment and automated CI/CD.

## Academic Integrity Notice

The primary research source is:
> Ju, S.; Park, Y. "Provably Secure Lightweight Mutual Authentication and Key Agreement Scheme for Cloud-Based IoT Environments." Sensors, 2023, 23(24), 9766. DOI: 10.3390/s23249766.

- This project is a normalized implementation of the published paper.
- The ECC counterpart and proposed extensions are explicitly separated from the original protocol.
- The communication cost reported in the paper is treated as a published reference value, not as an experimentally measured value.
- The quantum threat analysis is a conceptual module for educational purposes; it does not implement Shor's or Grover's algorithms.

## Quick Start (Development)

### Backend
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn cryptomaka.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment (Docker)

To run the full stack using Docker Compose:

```bash
docker-compose up --build -d
```

Access the application at `http://localhost:8080`.

## Directory Structure

- `backend/`: FastAPI Python backend implementation.
- `frontend/`: React + Vite frontend application.
- `docs/`: Comprehensive project documentation.
- `tests/`: Automated test suites (unit, integration, security).
- `docker/`: Dockerfiles for deployment.
- `research/`: Directories for storing experiment configs, results, and figures.
