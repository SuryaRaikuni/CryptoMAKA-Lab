# Current State Audit

## Existing Files and Their Purpose
- `src/maka_ju_park.py`: Implements the normalized Ju-Park MAKA protocol (hash/XOR).
- `src/ecc_counterpart.py`: Implements the ECC (ECDH) counterpart for the protocol.
- `src/maka_skeleton.py`: Provides a generic skeleton for MAKA schemes, used by benchmarks.
- `src/round_trip_extension.py`: Proposes a reduced-round-trip extension (design sketch).
- `benchmark/benchmark.py`: Basic timing/communication benchmarking script.
- `benchmark/benchmark_head_to_head.py`: Comprehensive head-to-head performance benchmark comparing Ju-Park and ECC.
- `demo/faculty_demo_final.py`: A wrapper script orchestrating the execution of the other scripts for a faculty demonstration.
- `security/security_analysis.py`: Runs security simulations (replay, tampering, etc.) on the protocols.
- `security/security_comparison.py`: Compares security properties between MAKA and ECC.
- `quantum/quantum_demo.py`: A conceptual demonstration of the quantum threat (Shor/Grover) to these protocols.

## Problems Found
1. **Disconnected Scripts:** The codebase currently consists of standalone python scripts run via `subprocess.run`. It is not a cohesive software system.
2. **Missing Package Structure:** Code is scattered in `src`, `security`, `benchmark` without a proper Python package structure or `__init__.py` files.
3. **Hardcoded State:** State is not persisted; everything runs in memory in ad-hoc tests.
4. **Poor Observability:** Benchmarks and security tests just print to the console instead of returning structured data.
5. **Lack of Web Interface:** Currently a CLI-based orchestration instead of the requested web-based dashboard.
6. **No Dependencies Configured:** Missing `pyproject.toml` / `requirements.txt`.
7. **Implicit Workarounds:** Scripts rely on the current working directory to run correctly.

## What Will Be Reused
- The core cryptographic logic for Ju-Park (hash/XOR), ECC/ECDH, and the reduced round-trip extension.
- The conceptually designed security scenarios (replay, tampering, etc.).
- The conceptual quantum threat analysis.
- The logic calculating communication sizes and timing metrics.

## What Will Be Replaced
- The `demo/faculty_demo_final.py` will be replaced by the FastAPI backend and React frontend (CryptoMAKA Lab dashboard).
- Standalone print-based testing will be replaced with structured API returns and a formal pytest test suite.
- In-memory execution will be supported by a PostgreSQL database for persisting experiment results.
- CLI execution will be replaced by API-driven experiments.

## Migration Notes
- We will create a `backend` directory containing the FastAPI application.
- The `src` code will move to `backend/cryptomaka/protocols/`.
- The `security` logic will move to `backend/cryptomaka/security/`.
- Benchmarks will move to `backend/cryptomaka/benchmarks/`.
- `quantum` logic will move to `backend/cryptomaka/quantum/`.
- We will set up a modern `pyproject.toml` environment using FastAPI, SQLAlchemy, Pydantic, etc.
- A React-based `frontend` will be established using Vite.
