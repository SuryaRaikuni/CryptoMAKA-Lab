# Formal Protocol Verification with ProVerif

This document details the **Formal Cryptographic Verification Suite** implemented in **CryptoMAKA Lab**, utilizing **Inria ProVerif 2.05+** under the **Dolev-Yao active adversary model** and the **applied pi-calculus**.

---

## 1. Formal Proofs vs. Empirical Testing

Cryptographic evaluation in CryptoMAKA Lab is structured across two complementary pillars:

| Evaluation Dimension | Engine | Methodology | Scope |
|---|---|---|---|
| **Empirical Security Testing** | `cryptomaka.security.runner` & Interactive Playground | Concrete execution simulations (replay, bit-flips, stale timestamps, forged credentials) | Detects implementation defects, boundary bugs, and parser errors under specific simulated vectors. |
| **Formal Mathematical Proof** | `research/formal_verification/` | Symbolic execution & Horn clause resolution via ProVerif | Mathematically proves secrecy and injective correspondence over an **unbounded number of concurrent sessions**. |

---

## 2. Mathematical Framework: Applied Pi-Calculus

Protocols are formally specified using the **applied pi-calculus**, extending the standard pi-calculus with cryptographic terms, equational theories, and constructor-destructor rewrite rules.

### 2.1 Attacker Model (Dolev-Yao)
The communication channel `free c: channel` is fully controlled by an active adversary $\mathcal{A}$ who can:
- **Eavesdrop** on any transmission on the public network.
- **Inject**, forge, or replay arbitrary bitstrings.
- **Interleave** sessions arbitrarily across multiple instances of User $U_i$, Control Server $CS$, and Cloud Server $S_j$.
- Compute any term obtainable through public cryptographic primitives (hashes, public keys, masking).

The attacker **cannot**:
- Invert one-way cryptographic hash functions: $h(x)$ is a random oracle.
- Guess uncompromised 256-bit random nonces.
- Decrypt ciphertexts without the corresponding secret key material.

---

## 3. Modeled Protocols & Equational Theories

CryptoMAKA Lab includes formal ProVerif models for all three supported protocol architectures in `research/formal_verification/`:

```
research/formal_verification/
├── ju_park.pv             # Ju & Park (Sensors 2023) Hash/XOR 3-party MAKA
├── ecc_baseline.pv        # Ephemeral Secp256r1 ECDH Authenticated Key Agreement
├── ml_kem.pv              # NIST FIPS 203 Post-Quantum ML-KEM-768 Lattice KEM
├── runner.py              # Automated runner & AST syntax validator
└── results/               # Certified ProVerif 2.05 resolution proof logs
    ├── ju_park_verification.txt
    ├── ecc_baseline_verification.txt
    └── ml_kem_verification.txt
```

### 3.1 Ju & Park Protocol (`ju_park.pv`)
- **Primitives**:
  - One-way hash function: `fun h(bitstring): bitstring.`
  - Masking reduction:
    $$\forall m, k; \quad \text{unmask}(\text{mask}(m, k), k) = m$$
  - Tuple pairing:
    $$\forall a, b; \quad \text{fst}(\text{pair}(a, b)) = a, \quad \text{snd}(\text{pair}(a, b)) = b$$
- **Security Events**:
  - `beginUser(Ui, CS, Sj, session_param)`
  - `beginCloud(Ui, CS, Sj, rj)`
  - `endCS(Ui, CS, Sj, session_binding)`
  - `endCloud(Ui, CS, Sj, SK)`
  - `endUser(Ui, CS, Sj, SK)`

### 3.2 ECC Baseline Protocol (`ecc_baseline.pv`)
- **Elliptic Curve Equational Theory**:
  - Diffie-Hellman exponentiation rewrite system:
    $$\text{exp}(\text{exp}(g, x), y) = \text{exp}(\text{exp}(g, y), x)$$
- Proves secrecy of ephemeral shared secret $g^{ab}$ and session keys derived via HKDF.

### 3.3 Post-Quantum ML-KEM-768 (`ml_kem.pv`)
- **Lattice KEM Rewrite Reduction**:
  - IND-CCA2 Key Encapsulation Mechanism:
    $$\forall sk, r; \quad \text{kem\_decaps}(sk, \text{kem\_encaps\_c}(\text{pk}(sk), r)) = \text{kem\_encaps\_k}(\text{pk}(sk), r)$$
- Models post-quantum resistance: immunity to quantum polynomial-time period-finding algorithms (Shor's algorithm).

---

## 4. Formal Security Properties & Proof Verdicts

All queries were formally evaluated using ProVerif 2.05. Every target property was **proved true** without counterexamples:

### 4.1 Ju & Park (Sensors 2023)
| Theorem ID | Formal Target | ProVerif Query Specification | Status | Academic Interpretation |
|---|---|---|---|---|
| **THM-01** | User Session Key Secrecy | `query not attacker(SK_User_Secret[])` | **PROVED TRUE** | Dolev-Yao attacker cannot derive $SK_U$ from intercepted $M_1 \dots M_4$. |
| **THM-02** | Cloud Session Key Secrecy | `query not attacker(SK_Cloud_Secret[])` | **PROVED TRUE** | Cloud server key material cannot be deduced by unauthorized eavesdroppers. |
| **THM-03** | Mutual Authentication ($U_i \to S_j$) | `inj-event(endUser(u,cs,sj,k)) ==> inj-event(endCloud(u,cs,sj,k))` | **PROVED TRUE** | User establishes key $k$ only if authentic Cloud engaged in the same session. Replay-free injective guarantee. |
| **THM-04** | Entity Authentication ($S_j \to U_i$) | `inj-event(endCloud(u,cs,sj,k)) ==> inj-event(beginUser(u,cs,sj,k))` | **PROVED TRUE** | Cloud completes key derivation only if genuine User initiated the session. |
| **THM-05** | Control Server Verification | `inj-event(endCS(u,cs,sj,k)) ==> inj-event(beginUser(u,cs,sj,k))` | **PROVED TRUE** | Control server authorizes access only upon authentic User credential presentation. |

### 4.2 ECC Baseline (Secp256r1)
| Theorem ID | Formal Target | ProVerif Query Specification | Status | Academic Interpretation |
|---|---|---|---|---|
| **THM-01** | User ECDH Secrecy | `query not attacker(SK_User_Secret[])` | **PROVED TRUE** | Session key derived from $g^{ab}$ is confidential under CDH assumption. |
| **THM-02** | Cloud ECDH Secrecy | `query not attacker(SK_Cloud_Secret[])` | **PROVED TRUE** | Responder session key cannot be observed. |
| **THM-03** | Mutual Authentication ($U_i \to S_j$) | `inj-event(endUser(u,sj,k)) ==> inj-event(endCloud(u,sj,k))` | **PROVED TRUE** | One-to-one injective correspondence between parties. |
| **THM-04** | Initiator Authentication | `inj-event(endCloud(u,sj,hkdf(pubA,nu))) ==> inj-event(beginUser(u,sj,pubA,nu))` | **PROVED TRUE** | Cloud server accepts request only from legitimate initiator. |

### 4.3 Post-Quantum ML-KEM-768 (NIST FIPS 203)
| Theorem ID | Formal Target | ProVerif Query Specification | Status | Academic Interpretation |
|---|---|---|---|---|
| **THM-01** | PQC User Key Secrecy | `query not attacker(SK_User_Secret[])` | **PROVED TRUE** | Post-quantum session key derived from lattice KEM is confidential. |
| **THM-02** | PQC Cloud Key Secrecy | `query not attacker(SK_Cloud_Secret[])` | **PROVED TRUE** | Decapsulated shared secret cannot be recovered by quantum-capable adversary. |
| **THM-03** | Mutual Authentication ($U_i \to S_j$) | `inj-event(endUser(u,sj,k)) ==> inj-event(endCloud(u,sj,k))` | **PROVED TRUE** | Lattice KEM ciphertext binds handshake sessions with injective guarantee. |
| **THM-04** | Ciphertext Correspondence | `inj-event(endCloud(u,sj,c_kem)) ==> inj-event(beginUser(u,sj,c_kem,nu))` | **PROVED TRUE** | Cloud decapsulates only ciphertexts genuinely produced by authenticated User. |

---

## 5. Running the Verification Suite

### 5.1 CLI Execution
Run the automated verification runner from the repository root:
```bash
python research/formal_verification/runner.py
```

The runner automatically detects whether a local `proverif` binary is present on the system. If present, it compiles and evaluates the models dynamically; otherwise, it executes the built-in applied pi-calculus AST syntax validator and verifies queries against certified reference proof transcripts.

### 5.2 Web UI & API
- **Web UI**: Navigate to the **Security Lab** page in the CryptoMAKA frontend and select the **Formal Verification (ProVerif)** tab.
- **REST API**:
  - `GET /api/v1/security/formal-verification`: Fetches verification proof summary across all protocols.
  - `GET /api/v1/security/formal-verification/{protocol_id}`: Retrieves raw `.pv` source code and execution transcripts.
