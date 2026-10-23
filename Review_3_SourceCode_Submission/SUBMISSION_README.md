# Review 3 Submission: Complete Source Code & Reproduction Guide

**Project Title:** Post-Quantum Readiness of a Lightweight XOR+Hash Mutual Authentication Scheme: An ECC Comparison for Cloud-IoT  
**Author:** Surya Pratap Singh Raikuni (Reg. No: 24BYB1114)  
**Department:** B.Tech Cybersecurity, SCOPE, VIT Chennai  
**Faculty Supervisor:** Dr. Karthika V  

---

## 1. Project Directory Contents

This submission folder contains the complete, self-contained source code, benchmarks, test harness, configuration files, and container definitions:

```
Review_3_SourceCode_Submission/
├── backend/                       # Python FastAPI backend & core protocol engines
│   └── cryptomaka/
│       ├── protocols/
│       │   ├── ju_park.py         # Bitwise-normalized 4-pass XOR+Hash protocol (Ju & Park 2023)
│       │   ├── ecc.py             # Authenticated Ephemeral ECDH (NIST P-256 baseline)
│       │   ├── reduced_roundtrip.py # Proposed 3-pass round-trip optimized scheme
│       │   └── ml_kem.py          # Post-Quantum Module-Lattice KEM (NIST FIPS 203)
│       ├── api/                   # REST endpoints for live evaluation & demonstration
│       ├── core/                  # Cryptographic primitives, nonces, and security checks
│       └── schemas/               # Request/response data models
├── benchmark/                     # Automated benchmarking scripts (execution time & comm. bits)
├── frontend/                      # React / TypeScript interactive evaluation UI (no node_modules)
├── research/
│   └── results/                   # Experimental data (benchmark_baseline.json)
├── tests/                         # Automated test suite (replay, tamper, MITM, impersonation)
├── docker/ & deploy/              # Containerization and production deployment manifests
├── pyproject.toml                 # Package definition, tool configuration, and dependencies
├── compose.yaml                   # Docker Compose specification for one-click setup
├── QUICKSTART.md                  # Detailed local setup and execution guide
└── SUBMISSION_README.md           # This guide
```

---

## 2. System Requirements

- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS
- **Python:** Version 3.11 or 3.12+
- **Node.js (Optional, for web frontend):** v18+ or v20+ with npm
- **Docker & Docker Compose (Optional):** For containerized execution

---

## 3. How to Reproduce Experimental Results & Run Code

### Step 1: Environment Setup
Open a terminal (PowerShell / Bash) inside this directory:

```bash
# 1. Create a Python virtual environment
python -m venv .venv

# 2. Activate virtual environment:
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies in editable mode:
pip install -e ".[dev]"
```

---

### Step 2: Run Automated Security Attack & Integrity Tests
To execute the attack simulation suite (replay, delayed replay, packet tampering, and impersonation):

```bash
pytest -v
```

---

### Step 3: Reproduce Protocol Benchmarks
To run the automated benchmark comparing Ju-Park, ECC P-256, and Reduced Round-Trip:

```bash
python -m benchmark.benchmark
```
*Results will output to console and update `research/results/benchmark_baseline.json`.*

---

### Step 4: Run the Backend API Service
To start the live interactive backend server:

```bash
uvicorn cryptomaka.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation will be available at:  
👉 **http://127.0.0.1:8000/docs**

---

### Step 5 (Optional): Run Frontend UI
```bash
cd frontend
npm install
npm run dev
```
Access the UI dashboard at: **http://localhost:5173**

---

### Step 6 (Alternative): One-Command Docker Run
If Docker is installed:
```bash
docker compose up --build
```
Both backend (`http://localhost:8000`) and frontend (`http://localhost:3000`) will launch automatically.
