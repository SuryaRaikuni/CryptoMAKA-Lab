# Presentation Speaker Script & Slide-by-Slide Notes

**Presentation Title**: CryptoMAKA Lab — Empirical Evaluation & Post-Quantum Hardening of Lightweight Cloud-IoT MAKA  
**Candidate**: Surya Pratap Singh Raikuni (Reg No: 24BYB1114)  
**Department**: B.Tech Cybersecurity, VIT Chennai  
**Faculty Guide**: Dr. Karthika V  
**Target Event**: Review 3 Comprehensive Viva & Defense  

---

### Slide 1: Title & Candidature Overview
- **Opening Statement**: "Good morning, respected Dr. Karthika V and evaluation committee members. Today I am presenting Review 3 for my research project titled *CryptoMAKA Lab: Empirical Evaluation and Post-Quantum Hardening of Lightweight Cloud-IoT Mutual Authentication: A Reproducible Formal Analysis*."
- **Key Emphasis**: Mention student registration number `24BYB1114`, department of Cybersecurity, VIT Chennai, and mentor Dr. Karthika V.

### Slide 2: Research Problem & Background
- **Talking Points**:
  - Cloud-IoT ecosystems are expanding rapidly across smart healthcare, industrial automation, and utility metering.
  - Sensors operate over public wireless channels without inherent physical security.
  - Conventional asymmetric protocols (RSA, standard Diffie-Hellman) consume too much RAM, CPU cycles, and battery power for low-end microcontrollers.
  - Crucially, existing lightweight cryptographic proposals in academic journals frequently suffer from specification ambiguities, making them impossible to reproduce or verify independently.

### Slide 3: Concrete Research Objectives
- **Talking Points**:
  - Focus on the four defined pillars:
    1. Reconstructing and normalizing the published Ju-Park 2023 protocol.
    2. Constructing an ECC P-256 baseline for rigorous side-by-side comparison.
    3. Designing a novel 3-pass Reduced-Round-Trip extension.
    4. Conducting automated formal verification in ProVerif and integrating NIST FIPS 203 ML-KEM-768 for post-quantum evaluation.

### Slide 4: Literature Review & Baseline Analysis
- **Talking Points**:
  - Walk the panel through the summary table.
  - Contrast Ju-Park 2023 (symmetric hash/XOR) with RFC 8446 (TLS 1.3) and Challa et al.
  - Highlight that our platform is the only solution unifying classical symmetric, modern elliptic-curve, and post-quantum lattice primitives under a single empirical testbed.

### Slide 5: Identified Research Gaps & Proposed Solutions
- **Talking Points**:
  - Gap 1: Normalization deficit (resolved by 256-bit constant-time padding).
  - Gap 2: Lack of multi-radio LPWAN telemetry (resolved by wireless airtime and microjoule energy modeling).
  - Gap 3: Quantum Shor vulnerability (resolved by FIPS 203 lattice KEM integration).

### Slide 6: Proposed System Architecture
- **Talking Points**:
  - Walk through the three architectural tiers: Protocol Core Engine, Verification & Threat Engine, and Telemetry/Web Dashboard.
  - Emphasize the end-to-end integration from wire packets up to real-time React visualization.

### Slide 7: Ju-Park 2023 Protocol & Mathematical Normalization
- **Talking Points**:
  - Explain the 4-pass handshake sequence ($M1$ to $M4$).
  - Clarify the mathematical role of fuzzy extractor biometrics ($\sigma_i$) and dynamic pseudonyms ($PID_i^*$).
  - Explain our 256-bit bitwise normalization rules that ensure reproducible XOR parity.

### Slide 8: Proposed Novelty: Reduced-Round-Trip (3-Pass) Protocol
- **Talking Points**:
  - Detail our primary architectural contribution: eliminating the 4th message hop.
  - Explain how the Authentication Server aggregates tickets ($M3_{CS}$ and $M3_U$).
  - Emphasize the quantitative benefits: 25% fewer round trips, 25% lower wire payload, and 33% faster airtime in NB-IoT.

### Slide 9: Post-Quantum Cryptography Integration (ML-KEM-768)
- **Talking Points**:
  - Explain why classical ECC P-256 is vulnerable to Shor's algorithm ($O(\log N)$).
  - Introduce NIST FIPS 203 ML-KEM-768 based on Module Learning With Errors over polynomial rings.
  - Discuss the trade-off: 2.2 KB wire size vs quantum immunity.

### Slide 10: Formal Security Verification (ProVerif)
- **Talking Points**:
  - Present the formal proofs table: 13 out of 13 theorems successfully verified.
  - Point out that secrecy of session keys and mutual authentication (injective correspondence) are formally guaranteed under the Dolev-Yao threat model.

### Slide 11: Empirical Adversarial Attack Simulation
- **Talking Points**:
  - Review the 7 automated attack scenarios.
  - Highlight that bit-flipping tampering, stale timestamps (>5s), and replay attacks were 100% intercepted and rejected with sub-millisecond detection.

### Slide 12: Host CPU Benchmark Results
- **Talking Points**:
  - Discuss the execution time vs payload graph:
    - Proposed Reduced-RTT: 0.61 ms.
    - Ju-Park: 0.82 ms.
    - ML-KEM-768: 2.38 ms.
    - ECC P-256: 4.15 ms.

### Slide 13: IoT Wireless Latency & Embedded MCU Energy
- **Talking Points**:
  - Walk through the wireless airtime comparison across LoRaWAN, NB-IoT, LTE-M, and 5G.
  - Explain the embedded ARM Cortex-M4 energy budget ($E_{\text{comp}} + E_{\text{tx}}$) and the resulting multi-year coin cell battery projections.

### Slide 14: Comprehensive Baseline Comparison Scorecard
- **Talking Points**:
  - Summarize the multi-dimensional scorecard comparing all four schemes across latency, wire bytes, airtime, energy, PFS, and quantum safety.

### Slide 15: Conclusion & Mandatory Submission Deliverables
- **Closing Statement**:
  - "In conclusion, CryptoMAKA Lab delivers a comprehensive, academically verified research platform that bridges the gap between theoretical protocol design and real-world Cloud-IoT deployment.
  - All Review 3 mandatory deliverables—including the Presentation (.pptx), IEEE Paper Source and PDF, Source Code with 1-click reproduction, and Supplementary Files with 1000 synthetic traces and proof transcripts—are fully packaged and verified.
  - Thank you, Dr. Karthika V and committee members. I welcome your questions."
