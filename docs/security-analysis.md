# Security Analysis & Empirical Verification

This document details the security verification methodology of **CryptoMAKA Lab**, comparing the formal security properties published in Ju \& Park (Sensors 2023) against empirical attack simulations implemented in the test engine.

---

## 1. Formal Proofs vs. Empirical Testing Distinction

> **ACADEMIC NOTICE:**
> An empirical test result of **PASS** indicates that the software implementation resisted an automated simulated attack scenario under specific simulated inputs.
> Empirical tests do **NOT** constitute mathematical proof of security. Formal proofs (e.g., BAN Logic, Random Oracle Model (RoR), ProVerif, or Scyther verification) are published separately in the source paper (Ju \& Park, 2023).

---

## 2. Test Suite Vector Analysis

The automated test suite in `cryptomaka.security.runner` implements 7 test scenarios:

### 2.1 Replay Attack Resistance (`test_replay_attack`)
- **Simulation:** Eve intercepts message $M_1$ from a legitimate session. After the legitimate session completes, Eve injects the captured $M_1$ to the Cloud Server.
- **Protocol Resistance:** In Ju-Park, successful session establishment causes the Control Server to update the user's pseudonym:
  $$PID_i^* = PID_i \oplus H(PID_i \parallel r_k \parallel r_i)$$
  When the replayed $M_1$ arrives, the Control Server searches its database for $PID_i$, which has been consumed and replaced. The server rejects the replay with `"unknown PID"`.

### 2.2 Timestamp Freshness (`test_stale_timestamp`)
- **Simulation:** An attacker delays a valid message $M_1$ beyond the freshness threshold:
  $$|T_{current} - TS_1| > \Delta T \quad (\Delta T = 30\text{ s})$$
- **Protocol Resistance:** The receiving entity verifies freshness before evaluating any cryptographic MAC. Stale messages are rejected immediately, protecting server resources from denial-of-service and state-exhaustion attacks.

### 2.3 Parameter Tampering Resistance (`test_message_tampering`)
- **Simulation:** Eve intercepts $M_1$ and flips one bit in the masked nonce payload $B_1$.
- **Protocol Resistance:** The user authenticator $V_1 = H(ID_{CS} \parallel TS_1 \parallel SID_i \parallel k_i \parallel r_i)$ binds the unmasked nonce $r_i$ to the message. The Control Server reconstructs $r_i' = B_1' \oplus H(SID_i \parallel ID_{CS} \parallel k_i)$ and compares $H(ID_{CS} \parallel TS_1 \parallel SID_i \parallel k_i \parallel r_i')$ with $V_1$. HMAC comparison fails in constant time.

### 2.4 User Impersonation Resistance (`test_user_impersonation`)
- **Simulation:** An attacker with an invalid pseudonym attempts to forge $M_1$.
- **Protocol Resistance:** The Control Server rejects unknown pseudo-identities without proceeding to costly computations, preserving server integrity.

### 2.5 Cloud Server Spoofing Resistance (`test_mitm_cloud_impersonation`)
- **Simulation:** An unauthorized rogue cloud server attempts to join the session.
- **Protocol Resistance:** The rogue cloud does not possess $k_j = H(ID_j \parallel x_{CS} \parallel n_j)$, so it cannot generate valid authenticator $V_2 = H(k_j \parallel TS_2 \parallel ID_j \parallel r_j)$.

### 2.6 Ephemeral Nonce Freshness (`test_nonce_reuse`)
- **Simulation:** Evaluation of ephemeral randomness generation for $r_i, r_j, r_k$.
- **Protocol Resistance:** System cryptographically generates 256-bit fresh nonces using OS CSPRNG (`os.urandom(32)`), guaranteeing uniqueness with probability $1 - 2^{-256}$.

### 2.7 Session Key Agreement Positive Control (`test_session_key_agreement`)
- **Simulation:** Positive control baseline ensuring that under uncorrupted channels, both User and Cloud Server derive identical session keys $SK_{user} == SK_{cloud}$ without leakage.
- **Verification:** Verified via strict byte equality check. Session keys are never logged or stored.
