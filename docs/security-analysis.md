# Security Analysis & Empirical Verification

This document details the security verification methodology of **CryptoMAKA Lab**, comparing the formal security properties published in Ju \& Park (Sensors 2023) against empirical attack simulations implemented in the test engine.

---

## 1. Formal Proofs vs. Empirical Testing Distinction

> **ACADEMIC NOTICE:**
> An empirical test result of **PASS** indicates that the software implementation resisted an automated simulated attack scenario under specific simulated inputs.
> Empirical tests do **NOT** constitute mathematical proof of security. Formal proofs (e.g., BAN Logic, Random Oracle Model (RoR), ProVerif, or Scyther verification) are published separately in the source paper (Ju \& Park, 2023).

---

## 2. Test Suite Vector Analysis & Attack Matrix

The automated test suite in `cryptomaka.security.runner` implements 7 active threat evaluations against the protocol state machines:

| Test ID | Threat Vector | Target Protocol Entity | Injected Fault / Manipulation | Expected Outcome | Protocol Defense Mechanism |
|---|---|---|---|---|---|
| **SEC-01** | Replay Attack | Cloud / Control Server | Resend intercepted $M_1$ after valid session terminates | **REJECT** (`unknown PID`) | Dynamic Pseudonym Rotation ($PID_i^* = PID_i \oplus H(PID_i \parallel r_k \parallel r_i)$) |
| **SEC-02** | Stale Timestamp | User / Cloud / Control | Advance message timestamp by $\pm 60\text{ s}$ ($> 30\text{ s}$) | **REJECT** (`stale timestamp`) | Explicit Timestamp Freshness Window Check ($\Delta T \le 30\text{ s}$) |
| **SEC-03** | Parameter Tampering | Control Server | Flip single bit in masked nonce $B_1$ or $B_2$ | **REJECT** (`authenticator mismatch`) | Cryptographic Binding in Authenticator $V_1$ via SHA-256 |
| **SEC-04** | User Impersonation | Control Server | Submit $M_1$ with unregistered random pseudo-identity | **REJECT** (`invalid identity/credentials`) | Registration Record Lookup Failure in Control Server Store |
| **SEC-05** | Cloud Impersonation | Control Server | Rogue Cloud sends $M_2$ without valid secret key $k_j$ | **REJECT** (`cloud verification failed`) | Authenticator $V_2$ keyed with cloud secret $k_j = H(ID_j \parallel x_{CS} \parallel n_j)$ |
| **SEC-06** | Nonce Reuse | Cryptographic PRNG | Verify that nonces $r_i, r_j, r_k$ are fresh per invocation | **PASS** (Zero collisions) | OS CSPRNG (`os.urandom(32)`) guarantees 256-bit entropy |
| **SEC-07** | Key Agreement Control | User & Cloud | Normal protocol exchange over clean channel | **PASS** ($SK_{user} == SK_{cloud}$) | Dual-ended evaluation of $SK = H(C_1 \parallel r_i \parallel r_j \parallel r_k)$ |

---

## 3. Detailed Vector Mechanics

### 3.1 Replay Attack Resistance (`SEC-01: test_replay_attack`)
- **Simulation:** Eve intercepts message $M_1$ from a legitimate session. After the legitimate session completes, Eve injects the captured $M_1$ to the Cloud Server.
- **Protocol Resistance:** In Ju-Park, successful session establishment causes the Control Server to update the user's pseudonym:
  $$PID_i^* = PID_i \oplus H(PID_i \parallel r_k \parallel r_i)$$
  When the replayed $M_1$ arrives, the Control Server searches its database for $PID_i$, which has been consumed and replaced. The server rejects the replay with `"unknown PID"`.

### 3.2 Timestamp Freshness (`SEC-02: test_stale_timestamp`)
- **Simulation:** An attacker delays a valid message $M_1$ beyond the freshness threshold:
  $$|T_{current} - TS_1| > \Delta T \quad (\Delta T = 30\text{ s})$$
- **Protocol Resistance:** The receiving entity verifies freshness before evaluating any cryptographic MAC. Stale messages are rejected immediately, protecting server resources from denial-of-service and state-exhaustion attacks.

### 3.3 Parameter Tampering Resistance (`SEC-03: test_message_tampering`)
- **Simulation:** Eve intercepts $M_1$ and flips one bit in the masked nonce payload $B_1$.
- **Protocol Resistance:** The user authenticator $V_1 = H(ID_{CS} \parallel TS_1 \parallel SID_i \parallel k_i \parallel r_i)$ binds the unmasked nonce $r_i$ to the message. The Control Server reconstructs $r_i' = B_1' \oplus H(SID_i \parallel ID_{CS} \parallel k_i)$ and compares $H(ID_{CS} \parallel TS_1 \parallel SID_i \parallel k_i \parallel r_i')$ with $V_1$. HMAC comparison fails in constant time.

### 3.4 User Impersonation Resistance (`SEC-04: test_user_impersonation`)
- **Simulation:** An attacker with an invalid pseudonym attempts to forge $M_1$.
- **Protocol Resistance:** The Control Server rejects unknown pseudo-identities without proceeding to costly computations, preserving server integrity.

### 3.5 Cloud Server Spoofing Resistance (`SEC-05: test_mitm_cloud_impersonation`)
- **Simulation:** An unauthorized rogue cloud server attempts to join the session.
- **Protocol Resistance:** The rogue cloud does not possess $k_j = H(ID_j \parallel x_{CS} \parallel n_j)$, so it cannot generate valid authenticator $V_2 = H(k_j \parallel TS_2 \parallel ID_j \parallel r_j)$.

### 3.6 Ephemeral Nonce Freshness (`SEC-06: test_nonce_reuse`)
- **Simulation:** Evaluation of ephemeral randomness generation for $r_i, r_j, r_k$.
- **Protocol Resistance:** System cryptographically generates 256-bit fresh nonces using OS CSPRNG (`os.urandom(32)`), guaranteeing uniqueness with probability $1 - 2^{-256}$.

### 3.7 Session Key Agreement Positive Control (`SEC-07: test_session_key_agreement`)
- **Simulation:** Positive control baseline ensuring that under uncorrupted channels, both User and Cloud Server derive identical session keys $SK_{user} == SK_{cloud}$ without leakage.
- **Verification:** Verified via strict byte equality check. Session keys are never logged or stored.
