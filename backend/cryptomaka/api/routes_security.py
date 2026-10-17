"""Security test API routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from cryptomaka.database import ProtocolRun, SecurityTestResult, get_db
from cryptomaka.schemas.security import (
    FormalModelDetailResponse,
    FormalVerificationResponse,
    PlaygroundSamplePacketResponse,
    PlaygroundTamperRequest,
    PlaygroundTamperResponse,
    SecurityRunRequest,
    SecurityRunResponse,
)
from cryptomaka.security.runner import run_all_security_tests

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/run", response_model=SecurityRunResponse)
def run_security_tests(
    request: SecurityRunRequest,
    db: Session = Depends(get_db),
):
    """Run the full security test suite against a protocol."""
    allowed = {"ju_park"}
    if request.protocol not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Security tests currently only support: {allowed}",
        )

    run_id = str(uuid.uuid4())

    # Create a protocol run record for this security test session
    db_run = ProtocolRun(
        id=run_id,
        protocol=request.protocol,
        status="security_test",
        authentication_success=False,
        session_key_match=False,
        implementation_version="0.1.0",
    )
    db.add(db_run)
    db.flush()

    # Execute the tests
    report = run_all_security_tests(request.protocol)

    # Persist individual results
    for result in report["results"]:
        db_result = SecurityTestResult(
            run_id=run_id,
            test_name=result["test"],
            status=result["status"],
            description=result["description"],
            evidence=result["evidence"],
            severity=result["severity"],
        )
        db.add(db_result)

    db_run.status = "complete"
    db.commit()

    return SecurityRunResponse(
        run_id=run_id,
        protocol=report["protocol"],
        total=report["total"],
        passed=report["passed"],
        failed=report["failed"],
        disclaimer=report["disclaimer"],
        results=report["results"],
    )


@router.get("/results")
def list_security_results(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Return the most recent security test results."""
    results = (
        db.query(SecurityTestResult)
        .order_by(SecurityTestResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "run_id": r.run_id,
            "test_name": r.test_name,
            "status": r.status,
            "description": r.description,
            "evidence": r.evidence,
            "severity": r.severity,
            "created_at": r.created_at.isoformat(),
        }
        for r in results
    ]


@router.get("/playground/sample-packet", response_model=PlaygroundSamplePacketResponse)
def get_playground_sample_packet(protocol: str = "ju_park"):
    """Fetch sample packet and tampering parameters for the Interactive Security Playground."""
    from cryptomaka.security.playground import get_sample_packet
    allowed = {"ju_park", "ecc", "ml_kem"}
    if protocol not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Playground protocol must be one of: {list(allowed)}",
        )
    return get_sample_packet(protocol)


@router.post("/playground/simulate", response_model=PlaygroundTamperResponse)
def simulate_playground_tampering(request: PlaygroundTamperRequest):
    """Execute an adversarial tamper simulation and return detailed verification telemetry."""
    from cryptomaka.security.playground import simulate_tamper
    allowed = {"ju_park", "ecc", "ml_kem"}
    if request.protocol not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Playground protocol must be one of: {list(allowed)}",
        )
    return simulate_tamper(request)


@router.get("/formal-verification", response_model=FormalVerificationResponse)
def get_formal_verification_summary(
    engine: str = Query("proverif", pattern="^(proverif|tamarin|scyther)$"),
):
    """
    Retrieve formal verification proof results evaluated across Ju-Park, ECC, and ML-KEM
    using the specified formal verification engine (proverif, tamarin, or scyther).
    """
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from research.formal_verification.runner import ENGINES_INFO, FormalVerificationRunner

    runner = FormalVerificationRunner()
    results = runner.verify_all(engine=engine)
    has_binary = runner.has_engine_binary(engine)
    engine_meta = ENGINES_INFO.get(engine, {})

    return FormalVerificationResponse(
        engine=engine_meta.get("name", engine),
        version=engine_meta.get("version", "1.0+"),
        has_binary=has_binary,
        engine_id=engine,
        supported_engines=runner.get_supported_engines(),
        results={k: v.to_dict() for k, v in results.items()},
    )


@router.get("/formal-verification/{protocol_id}", response_model=FormalModelDetailResponse)
def get_formal_verification_model_detail(
    protocol_id: str,
    engine: str = Query("proverif", pattern="^(proverif|tamarin|scyther)$"),
):
    """
    Retrieve raw model source code and certified execution proof transcript for a specific
    protocol and verification engine (proverif, tamarin, or scyther).
    """
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from research.formal_verification.runner import ENGINE_MODELS, FormalVerificationRunner

    if engine not in ENGINE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Engine '{engine}' not supported. Available: {list(ENGINE_MODELS.keys())}",
        )

    if protocol_id not in ENGINE_MODELS[engine]:
        raise HTTPException(
            status_code=404,
            detail=f"Protocol model '{protocol_id}' not found for engine '{engine}'. Available: {list(ENGINE_MODELS[engine].keys())}",
        )

    runner = FormalVerificationRunner()
    model_file = ENGINE_MODELS[engine][protocol_id]
    source_code = runner.get_model_source(protocol_id, engine=engine)
    transcript = runner.get_transcript(protocol_id, engine=engine)

    return FormalModelDetailResponse(
        protocol_id=protocol_id,
        engine=engine,
        model_file=model_file,
        source_code=source_code,
        transcript=transcript,
    )


