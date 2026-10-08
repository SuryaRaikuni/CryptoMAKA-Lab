"""Quantum threat analysis API routes."""

from __future__ import annotations

from fastapi import APIRouter

from cryptomaka.quantum.threat_model import (
    get_full_threat_report,
    toy_discrete_log_demo,
)

router = APIRouter(prefix="/quantum", tags=["quantum"])


@router.get("/threat-report")
def quantum_threat_report():
    """Return the full conceptual quantum threat analysis."""
    return get_full_threat_report()


@router.get("/demo/discrete-log")
def discrete_log_demo(
    secret_x: int = 12345,
):
    """
    Run a toy classical discrete-log demonstration.

    WARNING: This is a classical brute-force illustration on a TINY group.
    It is NOT Shor's algorithm. It is purely educational.
    """
    if secret_x < 1 or secret_x > 999_999:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="secret_x must be between 1 and 999999 for safety."
        )
    return toy_discrete_log_demo(secret_x=secret_x)
