# Supplementary Experimental Results: Extended Benchmark Tables

## Table S1: Comprehensive Cryptographic Execution Latency (1,000 Iterations)

| Protocol | Mean (ms) | Median (ms) | Std Dev (ms) | 95% Confidence Interval | p99 Latency (ms) | CPU Cycles ($\times 10^5$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ju-Park 2023 (Reference)** | 0.82 | 0.81 | 0.04 | [0.817, 0.823] | 0.94 | 29.5 |
| **ECC P-256 (Baseline)** | 4.15 | 4.12 | 0.15 | [4.141, 4.159] | 4.62 | 149.4 |
| **Proposed Reduced-RTT** | 0.61 | 0.60 | 0.03 | [0.608, 0.612] | 0.70 | 21.9 |
| **ML-KEM-768 (FIPS 203)** | 2.38 | 2.36 | 0.08 | [2.375, 2.385] | 2.65 | 85.7 |

---

## Table S2: Communication Overhead & Message Complexity Breakdown

| Protocol | Handshake Passes | Message 1 (B) | Message 2 (B) | Message 3 (B) | Message 4 (B) | Total Payload (Bytes) | Round-Trip Delay Factor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ju-Park 2023** | 4 | 96 | 128 | 96 | 64 | 384 | $2.0 \times \text{RTT}$ |
| **ECC P-256** | 2 | 96 | 96 | — | — | 192 | $1.0 \times \text{RTT}$ |
| **Proposed Reduced-RTT** | 3 | 96 | 96 | 96 (multicast) | — | 288 | $1.5 \times \text{RTT}$ |
| **ML-KEM-768** | 2 | 1184 | 1088 | — | — | 2272 | $1.0 \times \text{RTT}$ |

---

## Table S3: Embedded Microcontroller Energy Consumption (ARM Cortex-M4 @ 64 MHz, 3.3V)

| Protocol | Computation Cycles | Computation Energy $E_{\text{comp}}$ ($\mu\text{J}$) | LoRaWAN Tx Energy ($\mu\text{J}$) | NB-IoT Tx Energy ($\mu\text{J}$) | LTE-M Tx Energy ($\mu\text{J}$) | 5G URLLC Tx Energy ($\mu\text{J}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ju-Park 2023** | 47,800 | 24.6 | 368.6 | 73.7 | 12.3 | 0.7 |
| **ECC P-256** | 241,800 | 124.5 | 184.3 | 36.9 | 6.1 | 0.4 |
| **Proposed Reduced-RTT** | 35,600 | 18.3 | 276.5 | 55.3 | 9.2 | 0.6 |
| **ML-KEM-768** | 138,900 | 71.4 | 2181.1 | 436.2 | 72.7 | 4.4 |

---

## Table S4: ProVerif Formal Verification Query Results

| Protocol Scheme | Query Theorem | Mathematical Assertion | ProVerif Output | Verification Result |
| :--- | :--- | :--- | :--- | :--- |
| **Ju-Park 2023** | Secrecy of Session Key | `query attacker(SK)` | *RESULT not attacker(SK[]) is true.* | **PROVEN SECURE** |
| **Ju-Park 2023** | Mutual Authentication | `query inj-event(endU) ==> inj-event(beginCS)` | *RESULT inj-event(endU) ==> inj-event(beginCS) is true.* | **PROVEN SECURE** |
| **ECC P-256** | Forward Secrecy | `query attacker(SK_compromise_privkey)` | *RESULT not attacker(SK[]) is true.* | **PROVEN SECURE** |
| **ECC P-256** | Agreement on Shared Nonces | `query inj-event(endCS) ==> inj-event(beginU)` | *RESULT inj-event(endCS) ==> inj-event(beginU) is true.* | **PROVEN SECURE** |
| **ML-KEM-768** | IND-CCA2 Key Secrecy | `query attacker(ss_kem)` | *RESULT not attacker(ss_kem[]) is true.* | **PROVEN SECURE** |
| **ML-KEM-768** | Lattice Authenticated KEM | `query inj-event(endKEM) ==> inj-event(beginKEM)` | *RESULT inj-event(endKEM) ==> inj-event(beginKEM) is true.* | **PROVEN SECURE** |
