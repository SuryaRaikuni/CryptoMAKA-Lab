"""Protocol execution API routes."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from cryptomaka.database import ProtocolRun, get_db
from cryptomaka.schemas.protocols import (
    ProtocolInfo,
    ProtocolRunResponse,
)

router = APIRouter(prefix="/protocols", tags=["protocols"])

PROTOCOLS: dict[str, ProtocolInfo] = {
    "ju_park": ProtocolInfo(
        id="ju_park",
        name="Ju-Park 2023 (Normalized Reconstruction)",
        description=(
            "Faithful normalized implementation of the lightweight MAKA protocol "
            "from Ju & Park, Sensors 2023, 23(24), 9766. Uses SHA-256 and XOR-based "
            "field masking. Three-party model: User, Cloud Server, Control Server."
        ),
        message_count=4,
        primitives=["SHA-256", "XOR", "Nonce", "Timestamp"],
        label="published",
    ),
    "ecc": ProtocolInfo(
        id="ecc",
        name="ECC/ECDH Counterpart",
        description=(
            "ECC/ECDH counterpart using NIST P-256 with ephemeral key pairs and "
            "HKDF-SHA256 session key derivation. This is NOT a reproduction of the "
            "Ju-Park paper; it is an experimental alternative using modern asymmetric primitives."
        ),
        message_count=2,
        primitives=["ECDH P-256", "HKDF-SHA256", "Nonce", "Timestamp"],
        label="ecc_counterpart",
    ),
    "reduced_roundtrip": ProtocolInfo(
        id="reduced_roundtrip",
        name="Proposed Reduced-Round-Trip Extension",
        description=(
            "PROPOSED EXTENSION — NOT PART OF JU-PARK (2023). "
            "Experimental 3-message optimization that combines the Control Server "
            "response into a single message for both Cloud and User. "
            "Requires formal security analysis before any security claim can be made."
        ),
        message_count=3,
        primitives=["SHA-256", "XOR", "Nonce", "Timestamp"],
        label="proposed_extension",
    ),
    "ml_kem": ProtocolInfo(
        id="ml_kem",
        name="ML-KEM-768 Post-Quantum Prototype (FIPS 203)",
        description=(
            "POST-QUANTUM PROTOTYPE — NOT a production implementation. "
            "Demonstrates a KEM-based MAKA flow using ML-KEM-768 wire sizes "
            "(PK=1184B, CT=1088B per NIST FIPS 203 Table 2) and SHA-3 family "
            "primitives (SHA3-256, SHA3-512, SHAKE-256) as specified in FIPS 203. "
            "For production use, replace with liboqs-python or OpenSSL oqs-provider."
        ),
        message_count=4,
        primitives=["SHA3-256", "SHA3-512", "SHAKE-256", "ML-KEM-768 (simulated)"],
        label="post_quantum_prototype",
    ),
}


@router.get("", response_model=list[ProtocolInfo])
def list_protocols():
    """List all available protocols."""
    return list(PROTOCOLS.values())


@router.post("/{protocol}/run", response_model=ProtocolRunResponse)
def run_protocol(
    protocol: str,
    db: Session = Depends(get_db),
):
    """Execute a single protocol run and persist the result."""
    if protocol not in PROTOCOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown protocol '{protocol}'. Available: {list(PROTOCOLS.keys())}",
        )

    run_id = str(uuid.uuid4())

    # Run the protocol
    result = _execute_protocol(protocol)

    # Persist to database
    db_run = ProtocolRun(
        id=run_id,
        protocol=protocol,
        status=result.get("status", "error"),
        authentication_success=result.get("authentication_success", False),
        session_key_match=result.get("session_key_match", False),
        duration_ms=result.get("timings", {}).get("total_ms"),
        message_count=result.get("message_count"),
        communication_bits=result.get("communication_bits"),
        implementation_version="0.1.0",
        messages_metadata=result.get("messages"),
        timings=result.get("timings"),
        error_message=result.get("error"),
    )
    db.add(db_run)
    db.commit()

    # Build response (never include session keys or secrets)
    messages = [
        {"name": m["name"], "direction": m["direction"], "size_bits": m.get("size_bits", 0)}
        for m in result.get("messages", [])
    ]

    return ProtocolRunResponse(
        run_id=run_id,
        protocol=protocol,
        status=result.get("status", "error"),
        participants=result.get("participants", 3),
        authentication_success=result.get("authentication_success", False),
        session_key_match=result.get("session_key_match", False),
        message_count=result.get("message_count", 0),
        messages=messages,
        timings=result.get("timings", {}),
        communication_bits=result.get("communication_bits"),
        notes=result.get("notes", []),
    )


def _execute_protocol(protocol: str) -> dict[str, Any]:
    """Execute the named protocol and return a structured result dict."""
    t_start = time.perf_counter_ns()

    if protocol == "ju_park":
        return _run_ju_park(t_start)
    elif protocol == "ecc":
        return _run_ecc(t_start)
    elif protocol == "reduced_roundtrip":
        from cryptomaka.protocols.reduced_roundtrip import run_reduced_protocol
        result = run_reduced_protocol()
        return result
    elif protocol == "ml_kem":
        return _run_ml_kem(t_start)
    else:
        raise ValueError(f"Unknown protocol: {protocol}")


def _run_ju_park(t_start: int) -> dict[str, Any]:
    from cryptomaka.benchmarks.communication import jupark_communication_report
    from cryptomaka.protocols.ju_park import run_protocol

    try:
        result = run_protocol()
    except Exception as exc:
        return {
            "status": "error",
            "authentication_success": False,
            "session_key_match": False,
            "error": str(exc),
            "timings": {"total_ms": (time.perf_counter_ns() - t_start) / 1e6},
        }

    t_end = time.perf_counter_ns()
    total_ms = (t_end - t_start) / 1e6
    comm = jupark_communication_report()

    messages = [
        {"name": "M1", "direction": "User → Cloud", "size_bits": 4 * 256 + 32},
        {"name": "M2", "direction": "Cloud → Control Server", "size_bits": 4 * 256 + 2 * 256 + 2 * 32},
        {"name": "M3", "direction": "Control Server → Cloud", "size_bits": 7 * 256 + 32},
        {"name": "M4", "direction": "Cloud → User", "size_bits": 4 * 256 + 32},
    ]

    return {
        "status": "success" if result.get("match") else "error",
        "participants": 3,
        "authentication_success": True,
        "session_key_match": result.get("match", False),
        "message_count": 4,
        "messages": messages,
        "timings": {"total_ms": round(total_ms, 4)},
        "communication_bits": comm["implementation_bits"],
        "notes": [
            "Normalized reconstruction of Ju & Park (Sensors 2023, 23, 9766).",
            "Session key value is not logged or returned.",
        ],
    }


def _run_ecc(t_start: int) -> dict[str, Any]:
    from cryptomaka.benchmarks.communication import ecc_communication_report
    from cryptomaka.protocols.ecc import ControlServerECC, ECCCloudServer, ECCUser

    rc = ControlServerECC()
    cs = ECCCloudServer("cloud-1")
    user = ECCUser("alice", "password123", "bio-template")

    user.register(rc)

    try:
        m1, a, private_u = user.start_login()
        m2, sk_server, _, reason = cs.respond_to_login(rc, user.user_id, m1)

        if m2 is None:
            raise RuntimeError(f"Cloud rejected login: {reason}")

        sk_user, user_reason = user.finish_login(a, private_u, m1, m2)
        match = sk_user is not None and sk_user == sk_server
    except Exception as exc:
        return {
            "status": "error",
            "authentication_success": False,
            "session_key_match": False,
            "error": str(exc),
            "timings": {"total_ms": (time.perf_counter_ns() - t_start) / 1e6},
        }

    t_end = time.perf_counter_ns()
    total_ms = (t_end - t_start) / 1e6
    comm = ecc_communication_report()

    messages = [
        {"name": "M1", "direction": "User → Cloud/RC", "size_bits": 520 + 128 + 32 + 256},
        {"name": "M2", "direction": "Cloud → User", "size_bits": 520 + 128 + 32 + 256},
    ]

    return {
        "status": "success" if match else "error",
        "participants": 3,
        "authentication_success": True,
        "session_key_match": match,
        "message_count": 2,
        "messages": messages,
        "timings": {"total_ms": round(total_ms, 4)},
        "communication_bits": comm["implementation_bits"],
        "notes": [
            "ECC/ECDH counterpart — NOT the Ju-Park protocol.",
            "Uses NIST P-256 + HKDF-SHA256.",
            "Session key value is not logged or returned.",
        ],
    }


def _run_ml_kem(t_start: int) -> dict[str, Any]:
    from cryptomaka.benchmarks.communication import mlkem_communication_report
    from cryptomaka.protocols.ml_kem import run_protocol

    try:
        result = run_protocol()
    except Exception as exc:
        return {
            "status": "error",
            "authentication_success": False,
            "session_key_match": False,
            "error": str(exc),
            "timings": {"total_ms": (time.perf_counter_ns() - t_start) / 1e6},
        }

    t_end = time.perf_counter_ns()
    total_ms = (t_end - t_start) / 1e6
    comm = mlkem_communication_report()

    # ML-KEM-768 message sizes (FIPS 203 Table 2)
    PK_BITS = 1184 * 8   # 9472 bits
    CT_BITS = 1088 * 8   # 8704 bits
    NONCE_BITS = 256
    TS_BITS = 32
    AUTH_BITS = 256
    UID_BITS = 64
    M1_BITS = UID_BITS + PK_BITS + NONCE_BITS + TS_BITS + AUTH_BITS

    messages = [
        {"name": "M1", "direction": "User → Cloud Server",               "size_bits": M1_BITS},
        {"name": "M2", "direction": "Cloud Server → Registration Centre", "size_bits": M1_BITS},
        {"name": "M3", "direction": "RC → Cloud (ciphertext + SK)",       "size_bits": CT_BITS + NONCE_BITS + TS_BITS + AUTH_BITS},
        {"name": "M4", "direction": "Cloud → User",                       "size_bits": CT_BITS + NONCE_BITS + TS_BITS + AUTH_BITS},
    ]

    return {
        "status": "success" if result.get("match") else "error",
        "participants": 3,
        "authentication_success": True,
        "session_key_match": result.get("session_key_match", False),
        "message_count": 4,
        "messages": messages,
        "timings": {"total_ms": round(total_ms, 4)},
        "communication_bits": comm["implementation_bits"],
        "notes": result.get("notes", []),
    }
