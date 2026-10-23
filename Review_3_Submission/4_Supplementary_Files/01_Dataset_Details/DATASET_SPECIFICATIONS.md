# Supplementary Dataset Specifications: Cloud-IoT MAKA Benchmark Suite

## 1. Dataset Overview

- **Dataset Identifier**: `CryptoMAKA-IoT-Bench-v1.0`
- **Creation Date**: October 2026
- **Principal Investigator**: Surya Pratap Singh Raikuni (Reg No: 24BYB1114)
- **Academic Mentor**: Dr. Karthika V
- **Institution**: Vellore Institute of Technology (VIT Chennai), Department of Cybersecurity
- **Evaluated Literature**: Ju, S.; Park, Y. *Provably Secure Lightweight Mutual Authentication and Key Agreement Scheme for Cloud-Based IoT Environments* (Sensors 2023)
- **Access Link**: Openly archived in local and repository releases under `Review_3_Submission/4_Supplementary_Files/01_Dataset_Details/`

## 2. Description and Methodology

This dataset comprises 1,000 synthetic microsecond-precision handshake execution traces across four comparative protocol implementations:
1. **Ju-Park 2023 Reference**: 4-message hash/XOR normalized protocol.
2. **ECC P-256 Baseline**: 2-message Ephemeral Elliptic Curve Diffie-Hellman handshake.
3. **Proposed Reduced-RTT Extension**: 3-message aggregated response protocol.
4. **Post-Quantum ML-KEM-768**: 2-message Module-Lattice-Based Key-Encapsulation Mechanism (NIST FIPS 203).

Measurements include host execution timing, communication wire byte metrics, simulated airtime transmission latencies across four standard IoT radio frequency profiles (LoRaWAN EU868, NB-IoT Band 20, LTE-M Cat-M1, 5G URLLC), and embedded microcontroller energy expenditure (ARM Cortex-M4 @ 64 MHz, 3.3V, 120mW RF transmit power).

## 3. Schema & Field Definitions

| Field Name | Data Type | Units | Description |
| :--- | :--- | :--- | :--- |
| `packet_id` | String | Identifier | Unique trace identifier (`PKT-0001` through `PKT-1000`) |
| `protocol` | String | Categorical | Evaluated cryptographic protocol scheme |
| `wireless_channel` | String | Categorical | Simulated radio layer profile (e.g., LoRaWAN, NB-IoT) |
| `rtt_passes` | Integer | Count | Total physical message passes required to establish session key |
| `computation_time_ms` | Float | Milliseconds | Host cryptographic execution latency |
| `payload_size_bytes` | Integer | Bytes | Aggregated protocol payload transmitted over the insecure channel |
| `airtime_latency_ms` | Float | Milliseconds | Physical channel transmission delay $(8 \times \text{payload} / \text{bitrate})$ |
| `mcu_computation_energy_uj`| Float | Microjoules ($\mu\text{J}$) | Cryptographic processing energy on ARM Cortex-M4 |
| `wireless_tx_energy_uj` | Float | Microjoules ($\mu\text{J}$) | Radio transmitter energy consumed during packet transmission |
| `total_handshake_energy_uj` | Float | Microjoules ($\mu\text{J}$) | Combined energy budget $(E_{\text{comp}} + E_{\text{tx}})$ |
| `security_status` | String | Status | Outcome of mutual authentication and session key derivation |
| `tamper_detected` | Boolean | True/False | Dolev-Yao bit-flip attack intercepted and rejected by recipient |
| `replay_detected` | Boolean | True/False | Outdated timestamp / reused nonce identified and rejected |

## 4. Hardware & Software Testbed

- **CPU**: AMD Ryzen / Intel Core x86_64 @ 3.6 GHz, 32 GB RAM, Ubuntu Linux / Windows 11
- **Embedded Target**: ARM Cortex-M4 MCU running at 64 MHz, 3.3V Core Voltage, active draw 15 mA
- **Software**: Python 3.12, cryptography 43.0, FastAPI 0.115, ReportLab 4.2, ProVerif 2.05
- **Deterministic Seed**: PRNG seeded with constant seed `42` for exact reproducibility.
