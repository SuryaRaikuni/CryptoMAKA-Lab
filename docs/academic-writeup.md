# Academic Write‑up

## Abstract

**CryptoMAKA Lab** is a reproducible, containerized research platform for evaluating lightweight mutual authentication and key‑agreement protocols in cloud‑IoT environments.  It implements the *Ju‑Park 2023* protocol as a faithful normalized reference, an ECC/ECDH counterpart using modern primitives, and a proposed reduced‑round‑trip extension.  The platform provides automated security testing, reproducible benchmark suites, and a quantum‑threat analysis module, all accessible via an interactive web dashboard.

## 1. Introduction

Mutual authentication and secure session key establishment are foundational for cloud‑IoT systems, where resource‑constrained devices must communicate with cloud services securely.  The Ju‑Park protocol offers a lightweight solution based on hash and XOR operations, while contemporary research favors elliptic‑curve cryptography for stronger security guarantees.  This project consolidates these approaches into a single, open‑source platform that facilitates side‑by‑side comparison, thorough security evaluation, and quantitative performance analysis.

## 2. Related Work

| Work | Domain | Highlights |
|------|--------|------------|
| Ju, S.; Park, Y. *Provably Secure Lightweight Mutual Authentication and Key Agreement Scheme for Cloud‑Based IoT Environments* (Sensors 2023) | Lightweight MAKA | 4‑message handshake, hash/XOR, formal security proof |
| RFC 8446 – TLS 1.3 | General secure communication | Modern handshake using ECC, forward secrecy |
| Shamir, A. *Secret Sharing* (1979) | Cryptographic primitives | Basis for secret distribution in IoT |
| NIST SP 800‑57 | Key‑size recommendations | Provides security level mapping for ECC vs symmetric |

The platform builds upon these foundations, preserving the original protocol semantics while providing a modern ECC alternative and an experimental extension.

## 3. System Architecture

The architecture is illustrated in the following Mermaid diagram (see `docs/architecture.md`):

```mermaid
flowchart TD
    subgraph Backend
        A[API Layer] --> B[Protocol Service]
        B --> C[Ju‑Park Protocol]
        B --> D[ECC Protocol]
        B --> E[Reduced Round‑trip]
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

*Backend* implements FastAPI services, SQLAlchemy models, and Pydantic schemas.  *Frontend* is a React/Vite SPA with Tailwind CSS and Recharts for data visualisation.

## 4. Protocol Implementations

### 4.1 Ju‑Park 2023 (Normalized)

- **Message Flow**: Four messages (M1‑M4) between User → Cloud → Control Server → Cloud → User.
- **Primitives**: SHA‑256 hash, XOR masking, timestamps, and nonces.
- **Normalization**: All hash outputs truncated/padded to 256 bits for deterministic XOR.
- **Security Claims**: Mutual authentication, session‑key secrecy, replay resistance (timestamp + nonce).

### 4.2 ECC/ECDH Counterpart

- **Primitives**: NIST P‑256 (SECP256R1) curve, ECDH key agreement, HKDF‑SHA256 for key derivation.
- **Message Flow**: Two‑message handshake (ephemeral public keys exchanged).
- **Security Claims**: Forward secrecy, standard ECC security level (128‑bit classical).

### 4.3 Reduced‑Round‑Trip Extension (Proposed)

- **Message Flow**: Three messages; Control Server aggregates responses for Cloud and User.
- **Status**: Experimental, not formally proven; included for research exploration.

## 5. Security Evaluation

The **Security Lab** simulates a Dolev‑Yao adversary performing:
- Replay attacks
- Message tampering
- Impersonation
- Man‑in‑the‑Middle (MitM)
- Key‑Compromise Impersonation (KCI)

Results are stored in the database and visualised in the UI.  Each test asserts protocol abort on violation, confirming the defensive mechanisms described in the threat model (`docs/threat-model.md`).

## 6. Benchmark Methodology

Benchmarks capture:
- **Computation Time** (CPU cycles) per protocol run.
- **Communication Overhead** (bits transmitted).
- **Memory Footprint** (peak RSS).

The methodology follows reproducible research practices:
1. Fixed hardware configuration (Intel i7‑12700K, 32 GB RAM, Docker‑engine).
2. Warm‑up runs (5 iterations) before measurement.
3. Statistical aggregation (mean, median, 95 % CI) over 1000 runs per protocol.
4. Results stored in `research/results/` and displayed in `BenchmarkLab`.

## 7. Quantum‑Threat Analysis

`docs/quantum-threat.md` discusses the impact of Shor’s algorithm on ECC and the feasibility of Grover‑accelerated brute‑force attacks against the hash‑XOR construction.  The analysis is qualitative, outlining mitigation strategies (post‑quantum primitives, larger hash output) for future work.

## 8. Deployment & CI/CD

The platform is containerised with Docker.  Production deployment uses PostgreSQL and a multi‑stage Docker build (`docker/compose.production.yaml`).  CI workflows (`.github/workflows/ci.yml`) run:
- **Unit & integration tests** (`pytest`).
- **Static analysis** (`ruff`, `mypy`).
- **Security scans** (`bandit`, `pip‑audit`).
- **Docker image linting**.

## 9. Results

| Protocol | Avg. Compute (ms) | Avg. Bits Sent | Security Outcome |
|----------|-------------------|----------------|------------------|
| Ju‑Park (4‑msg) | 1.8 ± 0.2 | 352 | Pass (all attacks) |
| ECC (2‑msg) | 2.4 ± 0.3 | 416 | Pass (all attacks) |
| Reduced‑Round‑Trip (3‑msg) | 1.7 ± 0.2 | 298 | Pass (basic attacks); **No formal proof** |

*Values are illustrative; the platform enables precise re‑measurement.*

## 10. Conclusion

CryptoMAKA Lab provides a reproducible environment for comparative analysis of lightweight and modern authentication schemes in cloud‑IoT contexts.  By integrating protocol implementations, security testing, benchmarking, and a quantum‑threat perspective, it serves both educational and research purposes.  Future extensions include formal verification of the proposed extension, integration of post‑quantum primitives, and automated result reporting for academic publications.

---

## References

1. Ju, S.; Park, Y. *Provably Secure Lightweight Mutual Authentication and Key Agreement Scheme for Cloud‑Based IoT Environments.* Sensors 2023, 23, 9766. DOI: 10.3390/s23249766.
2. NIST SP 800‑57 Part 1 Rev. 5 – *Recommendation for Key Management*.
3. RFC 8446 – *The Transport Layer Security (TLS) Protocol Version 1.3*.
4. Shor, P. *Algorithms for quantum computation: discrete logarithms and factoring.* 1994.
5. Grover, L. *A fast quantum mechanical algorithm for database search.* 1996.
