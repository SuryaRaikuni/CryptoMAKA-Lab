# Implementation & Cryptographic Parameter Configuration

## 1. Cryptographic Primitive Parameters

### 1.1 Ju-Park 2023 Protocol Primitives
- **Hash Function**: SHA-256 (256-bit output truncated/padded for bitwise parity).
- **Masking Mechanism**: XOR ($\oplus$) with deterministic 32-byte alignment.
- **Fuzzy Extractor**:
  - $\text{Gen}(\text{Bio}_i) \rightarrow (\sigma_i, \tau_i)$
  - $\text{Rep}(\text{Bio}_i', \tau_i) \rightarrow \sigma_i$
  - Metric: Hamming distance error tolerance $\le 12\%$.
- **Timestamp Threshold**: $\Delta T = 5.0$ seconds clock drift tolerance.
- **Nonce Space**: 128-bit CSPRNG (`os.urandom(16)`).

### 1.2 Elliptic Curve Cryptography (ECC P-256)
- **Curve**: NIST P-256 (secp256r1 / prime256v1).
- **Field Size**: $p = 2^{256} - 2^{224} + 2^{192} + 2^{96} - 1$.
- **Base Point Order**: $n \approx 2^{256}$.
- **Key Exchange**: Ephemeral Diffie-Hellman (ECDH).
- **Key Derivation Function**: HKDF-SHA256 (RFC 5869) with salt and application info string.
- **Security Level**: 128-bit symmetric equivalence.

### 1.3 Post-Quantum Cryptography (FIPS 203 ML-KEM-768)
- **Standard**: NIST FIPS 203 (Module-Lattice-Based Key-Encapsulation Mechanism).
- **Parameter Set**: ML-KEM-768 (NIST Security Category 3, AES-192 equivalent).
- **Ring**: $R_q = \mathbb{Z}_q[X] / (X^{256} + 1)$ with $q = 3329$.
- **Module Rank**: $k = 3$.
- **Noise Distribution**: Centered Binomial Distribution with $\eta_1 = 2, \eta_2 = 2$.
- **Encapsulation Public Key Size**: 1,184 bytes.
- **Ciphertext Size**: 1,088 bytes.
- **Shared Secret Size**: 32 bytes (256 bits).

---

## 2. Hardware and Software Environment Specifications

### 2.1 Benchmark Host Environment
- **Processor**: x86_64 High-Performance Multi-Core (AMD/Intel) @ 3.6 GHz base clock.
- **Memory**: 32 GB DDR4/DDR5 Dual-Channel RAM.
- **Operating System**: Linux Kernel 6.8 / Microsoft Windows 11 Enterprise.
- **Python Execution Engine**: CPython 3.12.6 with optimized C-bindings (`cryptography 43.0.1`, OpenSSL 3.3.2).

### 2.2 Embedded Microcontroller Target Profile (ARM Cortex-M4)
- **Target MCU**: STM32F4 / NRF52840 (ARM Cortex-M4 with FPU).
- **Core Clock Frequency**: 64 MHz.
- **Operating Voltage**: 3.3 V DC.
- **Active Current Draw (Compute)**: 15 mA ($P_{\text{comp}} = 49.5\text{ mW}$).
- **Sleep Current Draw**: $2.5\ \mu\text{A}$.
- **Radio Active Transmit Power**: $P_{\text{tx}} = 120\text{ mW}$ (NB-IoT/LTE-M power amplifier active).

---

## 3. IoT Wireless Physical Layer Channel Models

| Profile Name | Carrier / Standard | Channel Bandwidth | Typical Data Rate | Uplink Transmit Latency Equation |
| :--- | :--- | :--- | :--- | :--- |
| **LoRaWAN** | EU868 Band | 125 kHz (SF7) | 10 kbps | $T_{\text{air}} = \frac{8 \times \text{Bytes}}{10,000} \text{ s}$ |
| **NB-IoT** | 3GPP Rel 14 Band 20 | 180 kHz | 50 kbps | $T_{\text{air}} = \frac{8 \times \text{Bytes}}{50,000} \text{ s}$ |
| **LTE-M** | 3GPP Rel 13 Cat-M1 | 1.4 MHz | 300 kbps | $T_{\text{air}} = \frac{8 \times \text{Bytes}}{300,000} \text{ s}$ |
| **5G URLLC** | 3GPP Rel 16 Sub-6GHz | 20 MHz | 5,000 kbps | $T_{\text{air}} = \frac{8 \times \text{Bytes}}{5,000,000} \text{ s}$ |
