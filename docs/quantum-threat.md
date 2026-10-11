# Quantum Threat Model & Post-Quantum Analysis

This document provides a conceptual analysis of the post-quantum cryptographic security posture of the protocols implemented in **CryptoMAKA Lab**.

---

## 1. Academic Disclaimer

> **IMPORTANT:**
> This analysis is **conceptual and educational**. No large-scale, fault-tolerant quantum computer currently exists that can break 128-bit classical cryptographic primitives. Shor's algorithm has only been demonstrated experimentally on small toy numbers.
> CryptoMAKA Lab does **not** implement quantum simulation hardware. The toy discrete-log demo in `threat_model.py` is a classical brute-force demonstration on a 31-bit prime group to illustrate group-theoretic hardness principles for educational purposes.

---

## 2. Theoretical Quantum Threat Comparison

| Protocol / Primitive | Hardness Assumption | Quantum Algorithm | Theoretical Quantum Impact | PQC Migration Path |
|---|---|---|---|---|
| **Ju-Park 2023** (SHA-256 + XOR) | Hash Preimage \& PRF Security | Grover's Algorithm | **Moderate Threat** ($O(\sqrt{N})$ speedup). Effective security drops from 256 bits to $\sim 128$ bits. Remains secure against foreseeable quantum computers. | Increase hash/nonce length to 512 bits (SHA-512 / SHA3-512) for 256-bit quantum security margin. |
| **ECC / ECDH** (NIST P-256) | Elliptic Curve Discrete Logarithm Problem (ECDLP) | Shor's Algorithm | **Critical / Fatal Threat** ($O(\text{poly}(n))$ speedup). Solves ECDLP in polynomial time; completely breaks key exchange. | Replace ECDH with NIST-standardized Post-Quantum KEM: **ML-KEM (CRYSTALS-Kyber, FIPS 203)**. |
| **Proposed Extension** (3-Message) | Hash Preimage \& PRF Security | Grover's Algorithm | **Moderate Threat** (Identical to Ju-Park). | Symmetric key size expansion. |

---

## 3. Grover's Algorithm Impact on Lightweight Hash/XOR Schemes

Grover's algorithm provides a quadratic speedup for searching unsorted databases or inverting generic black-box functions:
- To find a secret input $x$ given $H(x)$, a classical search requires $O(2^n)$ operations.
- A quantum computer using Grover's search requires $O(2^{n/2})$ evaluations.

For **Ju-Park**:
- SHA-256 preimage security is reduced from 256 bits to **128 quantum bits**.
- 128 bits of post-quantum security is considered secure and compliant with current NIST guidelines.
- Therefore, lightweight hash/XOR schemes like Ju-Park exhibit post-quantum resilience compared to asymmetric schemes based on RSA or ECC.

---

## 4. Shor's Algorithm Impact on Asymmetric Counterparts

Shor's algorithm solves the discrete logarithm problem over abelian groups (including elliptic curve groups $E(\mathbb{F}_p)$) in polynomial time:
$$T_{\text{Shor}} = O((\log p)^3)$$

For **NIST P-256**:
- An attacker with a fault-tolerant quantum computer running approximately 2,330 logical qubits could recover the private scalar $d$ from ephemeral public keys $P_u, P_c$ during the session exchange.
- This invalidates the security of ECDH key exchange, requiring migration to lattice-based Key Encapsulation Mechanisms (ML-KEM).

---

## 5. Post-Quantum Migration Roadmaps for Cloud-IoT

As standards evolve towards post-quantum cryptography (FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA), IoT designers face a trade-off:

1. **Lightweight Symmetric / Hash-based Schemes (Ju-Park style):**
   - Natural resistance to Shor's algorithm due to reliance on hash functions and symmetric keys.
   - Low communication overhead (~4.2 kbits) and low power consumption suitable for edge microcontrollers.
   - Requires online or pre-shared key infrastructure.

2. **Lattice-Based Post-Quantum Schemes (ML-KEM-512 / Kyber):**
   - Eliminates need for trusted online third-party server during key exchange.
   - Significantly larger ciphertext and public key sizes (e.g., ~800 to 1,200 bytes per message), introducing transmission overhead and potential fragmentation on 6LoWPAN / Zigbee IoT links.

3. **Hybrid Deployments:**
   - Combining classical lightweight handshakes with post-quantum key encapsulation to guarantee defense-in-depth during the quantum transition period.
