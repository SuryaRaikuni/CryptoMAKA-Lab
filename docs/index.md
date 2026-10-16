# CryptoMAKA Lab Documentation

Welcome to the **CryptoMAKA Lab** documentation portal.

CryptoMAKA Lab is an experimental, reproducible research platform for evaluating lightweight cloud-IoT mutual authentication and key agreement (MAKA) protocols.

---

## Architecture & Design
- **[Architecture Overview](architecture.md)** — Monorepo layout, modular backend services, database schema, and frontend SPA structure.
- **[Deployment Guide](deployment.md)** — Containerized multi-stage Docker builds, Docker Compose, and cloud deployment.

## Protocols & Cryptography
- **[Protocol Specifications](protocol.md)** — Mathematical formulations, message sequences, and normalization for Ju-Park (Sensors 2023), ECC/ECDH P-256 baseline, and Reduced-Roundtrip extensions.
- **[Quantum Threat Analysis](quantum-threat.md)** — Analysis of Shor's and Grover's algorithms against symmetric and asymmetric schemes, plus NIST post-quantum migration pathways (FIPS 203/204).

## Security & Verification
- **[Threat Model](threat-model.md)** — Dolev-Yao attacker capabilities, session corruption models, and credential exposure scenarios.
- **[Security Analysis](security-analysis.md)** — Matrix of 7 automated attack vectors (Replay, Stale Timestamp, Tampering, Impersonation, MitM, Nonce reuse, Session Key match) and verification results.

## Benchmarks & Research
- **[Benchmark Methodology](benchmark-methodology.md)** — High-resolution timing methodology (`perf_counter_ns`), statistical aggregation, and communication overhead breakdown.
- **[Academic Write-up](academic-writeup.md)** — Formatted research manuscript suitable for academic review, faculty evaluation, and conference submissions.
- **[Faculty Viva & Demo Guide](faculty-demo.md)** — Structured presentation outline, step-by-step demo flow, and common viva Q&A.
- **[Final Verification Report](final-verification.md)** — Comprehensive test matrix, security simulation findings, and quality audit sign-off.

---

*For rapid local setup, see the **[Quick Start Guide](../QUICKSTART.md)** or the main **[README](../README.md)**.*
