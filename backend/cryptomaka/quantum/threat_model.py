"""
Quantum threat analysis module for CryptoMAKA Lab.

IMPORTANT DISCLAIMERS:
1. This is a CONCEPTUAL RESEARCH MODULE. It does not implement Shor's algorithm.
2. No practical quantum computer currently threatens P-256 or SHA-256.
3. The toy discrete-log demonstration is a classical brute-force illustration
   for educational purposes ONLY. It is NOT a quantum simulation.
4. Claims in this module are based on published theoretical analysis, not
   experimental quantum computing results.

References:
- Shor, P. W. (1994). Algorithms for quantum computation.
  FOCS 1994. doi:10.1109/SFCS.1994.365700
- Grover, L. K. (1996). A fast quantum mechanical algorithm for database search.
  STOC 1996. doi:10.1145/237814.237866
- NIST SP 800-208 (2020). Recommendation for Stateful Hash-Based Signature Schemes.
- NIST PQC Project: https://csrc.nist.gov/Projects/post-quantum-cryptography
"""

from __future__ import annotations

import time
from typing import Any


# ---------------------------------------------------------------------------
# Threat analysis data
# ---------------------------------------------------------------------------

QUANTUM_DISCLAIMER = (
    "This analysis is conceptual and educational. "
    "No practical large-scale fault-tolerant quantum computer currently exists "
    "that threatens P-256 or SHA-256. Shor's algorithm has been demonstrated "
    "only on very small problem instances. This module presents the theoretical "
    "security implications for research awareness."
)

THREAT_ANALYSIS = {
    "ecc_ecdh": {
        "algorithm": "ECDH on NIST P-256 (SECP256R1)",
        "classical_security_bits": 128,
        "hardness_assumption": "Elliptic Curve Discrete Logarithm Problem (ECDLP)",
        "quantum_threat": "HIGH",
        "relevant_quantum_algorithm": "Shor's Algorithm",
        "quantum_security_bits": 0,
        "explanation": (
            "ECDH relies on the hardness of the Elliptic Curve Discrete Logarithm Problem. "
            "Shor's algorithm, running on a sufficiently large fault-tolerant quantum computer, "
            "can solve ECDLP in polynomial time — effectively reducing security to zero. "
            "A P-256 key would require approximately 2,330 logical qubits with full error correction "
            "(Roetteler et al., 2017). No such computer exists today."
        ),
        "mitigation": "Replace with NIST PQC finalist algorithms: CRYSTALS-Kyber (KEM), CRYSTALS-Dilithium (signature).",
        "status": "Theoretically vulnerable; not currently broken.",
    },
    "sha256": {
        "algorithm": "SHA-256",
        "classical_security_bits": 128,  # collision resistance
        "hardness_assumption": "Preimage resistance, collision resistance",
        "quantum_threat": "MODERATE",
        "relevant_quantum_algorithm": "Grover's Algorithm",
        "quantum_security_bits": 128,
        "explanation": (
            "Grover's algorithm provides a quadratic speedup for unstructured search problems. "
            "For SHA-256 preimage search, this reduces the effective security from 256 bits "
            "to approximately 128 bits in an idealized model. This is still considered "
            "computationally infeasible for any foreseeable quantum computer. "
            "SHA-256 is generally considered quantum-resistant for practical purposes "
            "with current and near-term quantum hardware projections."
        ),
        "mitigation": "SHA-256 remains acceptable; SHA-3 or SHA-512 provide additional margin.",
        "status": "Reduced but still adequate security margin against quantum attack.",
    },
    "xor_operations": {
        "algorithm": "XOR-based lightweight operations (Ju-Park protocol)",
        "classical_security_bits": 128,
        "hardness_assumption": "Secrecy of master secret xcs and derived keys",
        "quantum_threat": "MODERATE",
        "relevant_quantum_algorithm": "Grover's Algorithm (key search)",
        "quantum_security_bits": 64,
        "explanation": (
            "The Ju-Park protocol's security relies primarily on SHA-256 for authentication "
            "and XOR for field masking. The XOR operations are not independently secure; "
            "their security derives from the hashed key material. Grover's algorithm "
            "applied to key search on 128-bit keys would reduce effective security to ~64 bits, "
            "which may fall below acceptable thresholds for long-term deployments."
        ),
        "mitigation": "Increase key sizes to 256 bits for 128-bit post-quantum security margin.",
        "status": "Theoretical concern; not currently exploitable.",
    },
}

COMPARISON_TABLE = [
    {
        "protocol": "Ju-Park (hash/XOR)",
        "primitive": "SHA-256, XOR",
        "classical_bits": 128,
        "quantum_bits": "~64–128",
        "threat_level": "Moderate",
        "notes": "Hash-based; survives with key size increase",
    },
    {
        "protocol": "ECC/ECDH (P-256)",
        "primitive": "ECDLP, HKDF",
        "classical_bits": 128,
        "quantum_bits": "~0",
        "threat_level": "High",
        "notes": "Broken by Shor's algorithm in polynomial time",
    },
    {
        "protocol": "Proposed Extension (reduced-roundtrip)",
        "primitive": "SHA-256, XOR",
        "classical_bits": 128,
        "quantum_bits": "~64–128",
        "threat_level": "Moderate",
        "notes": "Same primitives as Ju-Park; similar quantum considerations",
    },
]

PQC_RECOMMENDATIONS = [
    {
        "use_case": "Key Encapsulation (replace ECDH)",
        "algorithm": "CRYSTALS-Kyber (ML-KEM)",
        "nist_status": "NIST FIPS 203 (2024)",
        "security_level": "128–256 bit post-quantum",
    },
    {
        "use_case": "Digital Signatures",
        "algorithm": "CRYSTALS-Dilithium (ML-DSA)",
        "nist_status": "NIST FIPS 204 (2024)",
        "security_level": "128–256 bit post-quantum",
    },
    {
        "use_case": "Hash-based signatures",
        "algorithm": "SPHINCS+ (SLH-DSA)",
        "nist_status": "NIST FIPS 205 (2024)",
        "security_level": "128–256 bit post-quantum",
    },
]


# ---------------------------------------------------------------------------
# Toy classical discrete-log demonstration
# (NOT a quantum simulation — educational only)
# ---------------------------------------------------------------------------

def toy_discrete_log_demo(
    p: int = 2_147_483_647,
    g: int = 5,
    secret_x: int = 12345,
) -> dict[str, Any]:
    """
    Classical brute-force discrete log on a small prime group.

    This is a pedagogical illustration of the discrete logarithm problem.
    It is NOT Shor's algorithm. It demonstrates WHY small groups are insecure,
    and why P-256 requires a quantum algorithm (Shor) to threaten — classical
    brute force is completely infeasible for real ECC parameters.
    """
    y = pow(g, secret_x, p)
    start = time.perf_counter()

    recovered = None
    value = 1
    for x in range(min(p, 10_000_000)):  # Cap at 10M iterations for safety
        if value == y:
            recovered = x
            break
        value = (value * g) % p

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "label": "Toy classical discrete-log — NOT a quantum simulation",
        "disclaimer": (
            "This is a classical brute-force search on a deliberately small group. "
            "It illustrates the structure of the discrete logarithm problem. "
            "Real P-256 groups are astronomically larger and cannot be brute-forced "
            "classically. Shor's algorithm would be needed for a quantum attack on P-256."
        ),
        "parameters": {"p": p, "g": g, "y": y, "secret_x": secret_x},
        "recovered_x": recovered,
        "success": recovered == secret_x,
        "elapsed_ms": round(elapsed_ms, 3),
        "interpretation": (
            f"Classical brute force took {elapsed_ms:.2f}ms on a tiny group (p≈2^31). "
            "P-256 uses a group of size ≈2^256. Classical brute force is infeasible. "
            "A fault-tolerant quantum computer running Shor's algorithm would be required."
        ),
    }


def get_full_threat_report() -> dict[str, Any]:
    """Return the complete quantum threat analysis report."""
    return {
        "disclaimer": QUANTUM_DISCLAIMER,
        "threat_analysis": THREAT_ANALYSIS,
        "comparison_table": COMPARISON_TABLE,
        "pqc_recommendations": PQC_RECOMMENDATIONS,
        "current_status": (
            "As of 2024, no quantum computer exists that can break P-256 or SHA-256. "
            "NIST has standardized post-quantum algorithms (FIPS 203/204/205) for "
            "future-proofing. Migration planning is recommended for long-lived systems."
        ),
    }
