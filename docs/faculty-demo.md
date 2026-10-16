# Faculty Demonstration & Viva Guide

This document outlines a structured, step-by-step demonstration plan for faculty presentations, project reviews, and viva examinations for **CryptoMAKA Lab**.

---

## 1. Executive Summary & Objective

**CryptoMAKA Lab** is an experimental and reproducible cybersecurity research platform designed for cloud-IoT Mutual Authentication and Key Agreement (MAKA). It reproduces and normalizes the lightweight symmetric protocol proposed by Ju & Park (*Sensors*, 2023), provides an asymmetric NIST P-256 ECC/ECDH baseline, and introduces a 3-message reduced-roundtrip novelty protocol.

### Key Talking Points
- **Academic Fidelity**: Strict separation between the published academic equations, the normalized implementation, and novel extensions.
- **Reproducibility**: Microsecond-precision CPU benchmarks (`perf_counter_ns`), automated attack test suites, and Dockerized deployment.
- **Empirical Security**: Real-time Dolev-Yao threat simulations (replay, timestamp tampering, parameter alteration, impersonation).

---

## 2. Pre-Demo Setup Checklist

Ensure the environment is ready prior to presentation:

1. **Option A: Local Development Server**
   ```bash
   # Terminal 1: Backend
   python -m uvicorn cryptomaka.main:app --host 127.0.0.1 --port 8000 --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173` in a web browser.

2. **Option B: Full-Stack Docker Deployment**
   ```bash
   docker compose -f docker/compose.yaml up --build -d
   ```
   Open `http://localhost:8080`.

3. **Verify API Docs**: Ensure `http://localhost:8000/docs` (or `:8080/docs`) displays Swagger UI.

---

## 3. Demonstration Flow (10–15 Minutes)

```
[1. Architecture & Design] ──> [2. Protocol Execution] ──> [3. Security Lab Attacks]
                                                                     │
[6. Q&A / Academic Defense] <── [5. Quantum Threat Analysis] <── [4. Benchmarking Lab]
```

### Step 1: Architecture & Monorepo Overview (2 mins)
- **Visual Aid**: Open the Dashboard overview page.
- **Talking Points**:
  - Explain the 3-tier cloud-IoT model: **User ($U_i$)**, **Cloud Server ($CS$)**, and **IoT Sensing Device ($SD_j$)**.
  - Highlight the clean monorepo architecture: FastAPI backend with modular cryptographic engines, SQLite/PostgreSQL persistence, and a React/Tailwind frontend.

### Step 2: Protocol Execution & Sequence Lifelines (3 mins)
- **Action**: Navigate to **Protocol Simulator** (`/simulator`).
- **Demo Sequence**:
  1. Select **Ju-Park (2023)**.
  2. Click **Run Protocol**.
  3. Walk the evaluator through the 4-message sequence lifeline:
     - **Message 1 ($U_i \to CS$)**: $\{M_1, M_2, T_1\}$ — User initiates session using pseudonym masked with master secret.
     - **Message 2 ($CS \to SD_j$)**: $\{M_3, M_4, T_2\}$ — Cloud authenticates $U_i$ and dispatches challenge to IoT device.
     - **Message 3 ($SD_j \to CS$)**: $\{M_5, M_6, T_3\}$ — Device computes session key $SK$ and returns verification token.
     - **Message 4 ($CS \to U_i$)**: $\{M_7, T_4\}$ — Cloud notifies User that mutual authentication is established.
  4. Point out the shared session key generated: both $U_i$ and $SD_j$ compute identical 256-bit keys ($SK_{U_i} == SK_{SD_j}$).
  5. Select **Reduced Round-trip (Proposed Extension)** and demonstrate the 3-message optimization.

### Step 3: Security Lab & Automated Attack Simulation (3 mins)
- **Action**: Navigate to **Security Lab** (`/security`).
- **Talking Points**:
  - Emphasize the Dolev-Yao attacker model: the adversary controls the public wireless channel and can intercept, replay, alter, or inject traffic.
- **Demo Sequence**:
  1. Click **Run Security Test Suite**.
  2. Observe the automated test matrix across 7 attack vectors:
     - **Replay Attack**: Captured $M_1$ replayed in a subsequent session $\to$ **DETECTED & REJECTED** (nonce freshness check).
     - **Stale Timestamp**: Packet injected with expired timestamp $|T_c - T_1| > \Delta T$ $\to$ **DETECTED & REJECTED**.
     - **Message Tampering**: Single-bit flip in hash payload $M_2$ $\to$ **INTEGRITY FAILURE**.
     - **User Impersonation**: Attacker fabricates credentials without registration secret $\to$ **AUTHENTICATION REJECTED**.
     - **Session Key Agreement**: Verifies cryptographic equality $SK_{user} = SK_{device}$.
  3. Highlight: All tests return verifiable cryptographic failure codes rather than crashing the system.

### Step 4: Benchmark Lab & Quantitative Evaluation (3 mins)
- **Action**: Navigate to **Benchmark Lab** (`/benchmarks`).
- **Demo Sequence**:
  1. Configure iteration count (e.g., $N = 100$ runs).
  2. Click **Execute Benchmark Comparison**.
  3. Walk through the generated Recharts comparison graphs:
     - **Computation Overhead**: Contrast lightweight symmetric operations ($\sim 10$–$50\,\mu s$) with asymmetric ECC point multiplications ($\sim 1$–$3\,ms$).
     - **Communication Cost**: Show message payload sizes across protocols (Ju-Park: 224 bytes total; ECC: 288 bytes; Reduced: 160 bytes).
     - **Statistical Rigor**: Highlight mean ($\mu$), standard deviation ($\sigma$), median, min, and max execution times measured via `time.perf_counter_ns()`.

### Step 5: Conceptual Quantum Threat Module (2 mins)
- **Action**: Navigate to **Quantum Threat** (`/quantum`).
- **Talking Points**:
  - Explain the impact of quantum computing on modern cryptosystems:
    - **Shor's Algorithm**: Polynomial-time resolution of Discrete Logarithm Problem (ECDLP) $\implies$ **completely breaks** NIST P-256 ECC.
    - **Grover's Algorithm**: Quadratic speedup for unstructured search $\implies$ reduces SHA-256 collision/preimage security to 128-bit security, remaining **computationally secure**.
  - Show the interactive discrete-log search demonstration showcasing the exponential difficulty for classical vs. quantum models.
  - Present the NIST Post-Quantum Cryptography (PQC) migration roadmap (FIPS 203 ML-KEM / Kyber).

---

## 4. Frequently Asked Viva Questions & Answers

### Q1: Why did you implement both Ju-Park and ECC?
> **Answer**: Ju-Park is a symmetric, lightweight hash-and-XOR scheme optimized for microcontrollers with strict energy budgets. However, symmetric schemes require the cloud server to store pre-shared credentials. We implemented ECC P-256 to provide a standard asymmetric baseline with forward secrecy, enabling empirical cost-benefit trade-off analysis between computational overhead and trust architecture.

### Q2: What is the novelty in your "Reduced Round-trip" protocol?
> **Answer**: The published Ju-Park protocol requires 4 messages ($U \to CS \to SD \to CS \to U$). In our proposed extension, we pipelined verification so the cloud server can respond directly with mutual verification tokens in 3 messages, reducing message latency and round-trip delay by 25% without compromising the session key entropy.

### Q3: How do you prevent replay attacks when clocks drift?
> **Answer**: Every message combines a synchronized timestamp $T$ with a high-entropy random nonce $R$. The recipient enforces $|T_{current} - T_{received}| \le \Delta T$ (e.g., $\Delta T = 5\,\text{s}$). Nonces are stored in an active sliding replay cache; even if $T$ is valid, replayed nonces are rejected immediately.

### Q4: Why are communication costs reported from the paper different from raw payload bytes?
> **Answer**: Published academic papers calculate communication costs based on theoretical field sizes (e.g., 256-bit hashes, 32-bit timestamps). Real-world implementations often encapsulate data into JSON, Protobuf, or byte buffers. We explicitly separate and report both the published theoretical values and our concrete wire payload measurements in the documentation and benchmark suite.

### Q5: How did you verify the implementation?
> **Answer**: We implemented 53 automated unit and integration tests using `pytest`, code formatting with `ruff`, security static analysis with `bandit`, and automated PDF documentation generation in GitHub Actions CI.
