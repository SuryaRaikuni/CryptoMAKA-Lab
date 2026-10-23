# Faculty Review 3 — Comprehensive Defense & Viva Q&A Guide

**Candidate**: Surya Pratap Singh Raikuni (Reg No: 24BYB1114)  
**Program**: B.Tech Cybersecurity, VIT Chennai  
**Faculty Mentor / Reviewer**: Dr. Karthika V  
**Project**: CryptoMAKA Lab — Reproducible Evaluation of Lightweight Cloud-IoT Mutual Authentication & Key Agreement

---

## 1. Quick 2-Minute Elevator Pitch for Review 3

> "Respected Dr. Karthika V and Review Committee members, our project **CryptoMAKA Lab** addresses a fundamental challenge in Cloud-IoT deployments: providing mutual authentication and forward-secure session key establishment without exhausting constrained IoT devices or relying on unverified cryptographic claims.
>
> In Review 3, we present three major accomplishments:
> 1. **Complete Normalized Implementation & Empirical Profiling**: We implemented the reference Ju-Park 2023 protocol with full 256-bit bitwise normalization, an ECC P-256 counterpart, a proposed Reduced-Round-Trip 3-pass extension, and a Post-Quantum lattice-based protocol using NIST FIPS 203 ML-KEM-768.
> 2. **Rigorous Automated Security Verification**: We subjected all protocols to active Dolev-Yao adversary attacks (replay, bit-flipping, MitM, KCI) and formally verified session-key secrecy and authentication invariants in the **ProVerif** applied pi-calculus, alongside Tamarin and Scyther proofs.
> 3. **IoT Wireless Channel & Energy Modeling**: We quantified microjoule energy consumption on ARM Cortex-M4 and transmission airtime latencies across LoRaWAN, NB-IoT, LTE-M, and 5G.
>
> All code, IEEE paper source, datasets, and execution scripts are 100% reproducible and ready for deployment."

---

## 2. Anticipated Viva Questions & Precise Answers

### Q1: Why was it necessary to normalize the Ju-Park 2023 protocol? What was missing in the original paper?
**Answer**:
"In the original Sensors 202Sensors 2023 paper by Ju and Park, the equations abstractly execute XOR operations ($\oplus$) between hash values, random nonces, timestamps, and biometric credentials without explicitly defining output truncations or bit-padding rules. In an actual software or embedded deployment, mismatched byte lengths cause fatal bitwise exceptions. In CryptoMAKA Lab, we normalized all hash representations deterministically to 256 bits (32 bytes) with constant-time XOR masking, providing the first reproducible software reference."

### Q2: What is your proposed extension, and how does it reduce round trips?
**Answer**:
"The original Ju-Park protocol requires 4 sequential round-trip passes: $U \rightarrow CS \rightarrow AS \rightarrow CS \rightarrow U$. In low-power wide-area networks like LoRaWAN or NB-IoT, message handshakes suffer significant airtime latency. Our proposed Reduced-RTT extension aggregates the Control Server's response ticket into a single authenticated multi-party payload broadcast or simultaneous multicast ($M3_{CS}$ and $M3_U$), reducing the sequence to 3 passes. This achieves a **25% reduction in message transmission airtime** while maintaining formal secrecy under ProVerif."

### Q3: Why did you incorporate NIST FIPS 203 ML-KEM-768?
**Answer**:
"Classical protocols relying on discrete logarithms or elliptic curves (like ECC P-256) are completely broken by Shor's quantum algorithm ($O(\log N)$ polynomial time). Although symmetric XOR protocols like Ju-Park are resilient against Shor's algorithm, they lack asymmetric key encapsulation and forward secrecy. We integrated FIPS 203 ML-KEM-768 (Module-Lattice KEM) to evaluate the exact communication and energy penalty (2,272 bytes payload vs 384 bytes in Ju-Park) required for true post-quantum quantum-resistant IoT key exchange."

### Q4: How does your Dolev-Yao adversary simulate attacks?
**Answer**:
"We implemented an automated adversary engine that sits between the wire endpoints. It simulates:
- **Replay Attacks**: Capturing valid packets and replaying them outside the timestamp threshold $\Delta T = 5\text{s}$.
- **Message Tampering**: Flipping bit patterns in ciphertext $C_{CS}$ or authenticator hashes to verify immediate abort.
- **Impersonation**: Injecting forged identity nonces without knowledge of master secret $x$.
- **Key-Compromise Impersonation (KCI)**: Testing whether compromising the device's static key allows the attacker to impersonate an authentic server."

### Q5: How do the energy measurements translate to real IoT battery lifespans?
**Answer**:
"On an ARM Cortex-M4 running on a typical 2400 mAh IoT coin cell battery (CR2032 or Li-SOCl2):
- Ju-Park consumes only $24.6\ \mu\text{J}$ compute energy and $73.7\ \mu\text{J}$ on NB-IoT ($98.3\ \mu\text{J}$ total), allowing over **2.8 million handshakes** on a single battery charge.
- ML-KEM-768 requires $507.6\ \mu\text{J}$ total due to the 2.2 KB packet transmission, which is acceptable for high-security smart grid nodes or healthcare telemetry."
