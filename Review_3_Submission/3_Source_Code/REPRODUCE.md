# Reproduction Guide: CryptoMAKA Lab (Review 3 Submission)

**Candidate**: Surya Pratap Singh Raikuni (Reg No: 24BYB1114)  
**Program**: B.Tech Cybersecurity, VIT Chennai  
**Faculty Guide**: Dr. Karthika V  

This document provides instructions to execute, evaluate, and reproduce all experimental benchmarks, security tests, and formal verification proofs presented for Review 3.

---

## 1. Quick 1-Command Reproduction

From the repository root, run the master reproduction script:

```bash
python Review_3_Submission/4_Supplementary_Files/05_Supporting_Materials/run_all_evaluations.py
```

This automated script sequentially executes:
1. **Core Handshakes**: Ju-Park 2023 normalized, ECC P-256 counterpart, Proposed Reduced-RTT, and NIST FIPS 203 ML-KEM-768.
2. **Dolev-Yao Adversary Attacks**: 7 automated attack scenarios (replay, tampering, impersonation, MitM, nonce reuse, key agreement).
3. **Formal Verification Engine**: Validates 13 applied pi-calculus theorems across ProVerif models.
4. **IoT Wireless Channel & Energy Sim**: Models NB-IoT transmission airtimes and ARM Cortex-M4 microjoule energy consumption.

---

## 2. Interactive Web Application Setup

To launch the full interactive web dashboard (React + FastAPI + PostgreSQL/SQLite):

### Step A: Start the Backend REST API
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows PowerShell: .\.venv\Scripts\Activate.ps1

# Run FastAPI server
python -m uvicorn cryptomaka.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/api/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`

### Step B: Start the Frontend UI
```bash
cd frontend
npm install
npm run dev
```
- Open browser at `http://localhost:5173`
- Explore:
  - **Protocol Simulator**: Step-by-step visual handshake animations.
  - **Security Lab**: Interactive Dolev-Yao adversary attack playground.
  - **Benchmark Lab**: Real-time Recharts execution timing and communication charts.
  - **IoT Wireless & Energy Lab**: Channel latency and battery lifetime projections.
  - **Formal Verification Lab**: ProVerif applied pi-calculus code and live certified proofs.

---

## 3. Unit Test Execution

Run the complete 112-test automated unit test suite:

```bash
pytest tests/ -v
```

All 112 tests should pass with 100% green status.
