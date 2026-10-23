# Changelog

All notable changes to the **CryptoMAKA Lab** platform will be documented in this file.

## [0.1.0] - 2026-10-11

### Added
- **Faithful Normalized Ju-Park 2023 Protocol:** 3-party mutual authentication and key agreement reconstruction using SHA-256 and XOR field masking.
- **ECC/ECDH P-256 Counterpart:** Modern asymmetric baseline with ephemeral ECDH key pairs and HKDF-SHA256 session derivation.
- **Proposed Reduced-Roundtrip Extension:** Experimental 3-message optimization combining Cloud Server and User responses.
- **Automated Security Engine:** 7 automated attack vectors (Replay, Stale Timestamp, Tampering, Impersonation, MitM, Nonce reuse, Session Key match).
- **Benchmarking Suite:** Reproducible microsecond-precision benchmarks (`perf_counter_ns`), with statistical metrics ($\mu$, median, min, max, $\sigma$) and communication cost reporting.
- **Conceptual Quantum Threat Module:** Grover vs. Shor post-quantum analysis and educational discrete-log demonstration.
- **Interactive Web Dashboard:** React 18 + Vite + Tailwind CSS + Recharts SPA featuring live Protocol Flow sequence diagrams, Security Lab, Benchmark comparison charts, and Experiment History with CSV/JSON exports.
- **Deployment & CI:** Multi-stage Docker builds, Docker Compose (SQLite dev & PostgreSQL prod), Render cloud blueprint, and GitHub Actions CI workflow.
- **Comprehensive Documentation Suite:** `threat-model.md`, `security-analysis.md`, `benchmark-methodology.md`, `quantum-threat.md`, and LaTeX publication tables.

### Refactored
- Removed obsolete root-level prototype scripts (`src/`, `benchmark/`, `security/`, `quantum/`, `demo/`).
- Eliminated all `sys.path.insert` hacks in favor of standard Python packaging (`cryptomaka`).
