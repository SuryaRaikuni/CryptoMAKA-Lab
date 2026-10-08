# Protocol Documentation

## 1. Ju-Park 2023 (Normalized Reconstruction)

This implementation faithfully reconstructs the protocol proposed in:
> Ju, S.; Park, Y. "Provably Secure Lightweight Mutual Authentication and Key Agreement Scheme for Cloud-Based IoT Environments." Sensors, 2023, 23(24), 9766.

**Entities:**
* User (Device)
* Cloud Server ($S_j$)
* Control Server (CS)

**Primitives:**
* Hash functions (SHA-256)
* XOR for field masking
* Random nonces
* Timestamps for freshness

**Flow (4 Messages):**
1. M1: User $\rightarrow$ Cloud
2. M2: Cloud $\rightarrow$ Control Server
3. M3: Control Server $\rightarrow$ Cloud
4. M4: Cloud $\rightarrow$ User

*Note on Normalization*: Where notation in the paper was ambiguous regarding field widths, the implementation normalizes all hashed values to 256 bits (SHA-256 output size) to ensure correct XOR operation alignment.

## 2. ECC/ECDH Counterpart

An experimental alternative replacing the hash/XOR construction with modern asymmetric cryptography.

**Primitives:**
* NIST P-256 (SECP256R1) Elliptic Curve
* ECDH for key exchange
* HKDF-SHA256 for session key derivation

**Flow (2 Messages):**
1. M1: User $\rightarrow$ Cloud (Includes User's ephemeral public key)
2. M2: Cloud $\rightarrow$ User (Includes Cloud's ephemeral public key)

*Disclaimer*: This is not part of the Ju-Park paper.

## 3. Proposed Reduced-Round-Trip Extension

**PROPOSED EXTENSION — NOT PART OF JU-PARK 2023**

This is an experimental optimization that reduces the original 4-message flow to 3 messages by having the Control Server generate the authenticated responses for both the Cloud and the User simultaneously.

**Flow (3 Messages):**
1. M1: User $\rightarrow$ Cloud
2. M2: Cloud $\rightarrow$ Control Server
3. M3 (Combined): Control Server $\rightarrow$ Cloud $\rightarrow$ User

*Security Note*: This extension has not been formally analyzed and no security claims are made regarding its equivalence to the original protocol.
