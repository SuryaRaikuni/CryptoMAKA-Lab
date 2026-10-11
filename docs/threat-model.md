# Adversary and Threat Model

This document specifies the adversarial assumptions and threat model under which the Ju-Park (2023) lightweight MAKA protocol, the ECC/ECDH counterpart, and the proposed reduced-roundtrip extension are evaluated in **CryptoMAKA Lab**.

---

## 1. Dolev-Yao Threat Model

The network communication model follows the classical **Dolev-Yao** adversarial standard:
1. **Full Channel Control:** The adversary $\mathcal{A}$ has complete control over public communication channels connecting the User ($U_i$), Cloud Server ($S_j$), and Control Server ($CS$).
2. **Channel Capabilities:** $\mathcal{A}$ can intercept, drop, delay, modify, inject, and replay arbitrary messages ($M_1, M_2, M_3, M_4$).
3. **Cryptographic Assumptions:** Cryptographic primitives are treated as black boxes with idealized security properties:
   - SHA-256 acts as a cryptographically secure pseudo-random function (PRF) with preimage and collision resistance ($2^{128}$ classical security bits).
   - $\mathcal{A}$ cannot invert SHA-256 or compute XOR masks without possessing the underlying keys or secret nonces.

---

## 2. Entity and Credential Compromise Models

### 2.1 User Device / Smart Card Theft
- $\mathcal{A}$ may physically capture or extract the contents of a user's smart card ($SC_i$).
- The smart card contains stored parameters: $\{PID_i, A_1, A_2, ID_{CS}\}$.
- **Biometric / Fuzzy Verifier Assumption:** The user's biometric template $BIO_i$ and password $PW_i$ are protected by high-entropy masking ($RPW_i = H(ID_i \parallel PW_i \parallel \sigma_i)$).
- **Security Goal:** Extraction of smart card parameters must not allow offline password guessing or identity disclosure without simultaneously possessing the correct biometric helper parameter $\sigma_i$.

### 2.2 Untrusted / Semi-Honest Cloud Server ($S_j$)
- The Cloud Server is treated as honest-but-curious: it follows the protocol correctly to deliver services, but may attempt to infer user identities or eavesdrop on session secrets.
- **Security Goal:** $S_j$ should not learn the user's permanent identity $ID_i$ (ensuring user anonymity and pseudonymity).

### 2.3 Trusted Control Server ($CS$)
- The Control Server is the root trust anchor holding master key $x_{CS}$.
- Master secret $x_{CS}$ is kept securely in hardware/HSM and never revealed over the network.

---

## 3. Specific Attack Vectors Evaluated

| Threat Vector | Description | Countermeasure in Ju-Park Protocol |
|---|---|---|
| **Replay Attack** | $\mathcal{A}$ replays previously captured $M_1$ or $M_2$ | Timestamps ($TS_1, TS_2$) + dynamic pseudonym updating ($PID_i \rightarrow PID_i^*$) consumes the ticket |
| **Stale Timestamp** | $\mathcal{A}$ delivers valid message outside the freshness window | Verified against freshness threshold $\Delta T \le 30$ seconds |
| **Message Tampering** | $\mathcal{A}$ flips bits in transmission parameters ($B_1, B_2, B_3$) | Cryptographic MAC authenticators ($V_1, V_2, V_3, V_4$) detect modification |
| **Impersonation** | $\mathcal{A}$ fabricates authentication request without credentials | Requires knowledge of $SID_i$ and $k_i$, derived from secret $x_{CS}$ |
| **Man-in-the-Middle (MitM)** | $\mathcal{A}$ intercepts and attempts concurrent double-sided session key negotiation | Mutual key confirmation strings ($C_1, B_8, B_9$) enforce end-to-end agreement |
| **Session Key Recovery** | $\mathcal{A}$ attempts to derive session key $SK$ from public channel values | $SK = H(SID_i \parallel SID_j \parallel r_i \parallel r_j \parallel r_k)$ requires ephemeral nonces protected by XOR masks |
