"""Experiment management API routes."""

from __future__ import annotations

import csv
import io
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from cryptomaka.api.routes_protocols import _execute_protocol
from cryptomaka.database import Experiment, ProtocolRun, get_db
from cryptomaka.schemas.experiments import (
    ExperimentCreateRequest,
    ExperimentDetail,
    ExperimentSummary,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentDetail)
def create_experiment(
    request: ExperimentCreateRequest,
    db: Session = Depends(get_db),
):
    """Create an experiment and optionally run protocol + benchmark + security tests."""
    allowed = {"ju_park", "ecc", "reduced_roundtrip"}
    if request.protocol not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown protocol '{request.protocol}'. Must be one of: {allowed}",
        )

    exp_id = str(uuid.uuid4())
    exp = Experiment(
        id=exp_id,
        name=request.name,
        protocol=request.protocol,
        configuration=request.configuration,
    )
    db.add(exp)
    db.flush()

    runs = []

    # Always run one protocol execution
    run_id = str(uuid.uuid4())
    proto_result = _execute_protocol(request.protocol)
    db_run = ProtocolRun(
        id=run_id,
        experiment_id=exp_id,
        protocol=request.protocol,
        status=proto_result.get("status", "error"),
        authentication_success=proto_result.get("authentication_success", False),
        session_key_match=proto_result.get("session_key_match", False),
        duration_ms=proto_result.get("timings", {}).get("total_ms"),
        message_count=proto_result.get("message_count"),
        communication_bits=proto_result.get("communication_bits"),
        implementation_version="0.1.0",
        messages_metadata=proto_result.get("messages"),
        timings=proto_result.get("timings"),
        error_message=proto_result.get("error"),
    )
    db.add(db_run)
    runs.append({"run_id": run_id, "type": "protocol", **proto_result})

    db.commit()

    return ExperimentDetail(
        id=exp_id,
        name=request.name,
        protocol=request.protocol,
        created_at=exp.created_at,
        run_count=len(runs),
        configuration=request.configuration,
        runs=runs,
    )


@router.get("", response_model=list[ExperimentSummary])
def list_experiments(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Return the most recent experiments."""
    exps = (
        db.query(Experiment)
        .order_by(Experiment.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        ExperimentSummary(
            id=e.id,
            name=e.name,
            protocol=e.protocol,
            created_at=e.created_at,
            run_count=len(e.runs),
        )
        for e in exps
    ]


@router.get("/{exp_id}", response_model=ExperimentDetail)
def get_experiment(
    exp_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve a specific experiment by ID."""
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found")

    runs = [
        {
            "run_id": r.id,
            "protocol": r.protocol,
            "status": r.status,
            "authentication_success": r.authentication_success,
            "session_key_match": r.session_key_match,
            "duration_ms": r.duration_ms,
            "message_count": r.message_count,
            "created_at": r.created_at.isoformat(),
        }
        for r in exp.runs
    ]

    return ExperimentDetail(
        id=exp.id,
        name=exp.name,
        protocol=exp.protocol,
        created_at=exp.created_at,
        run_count=len(exp.runs),
        configuration=exp.configuration,
        runs=runs,
    )


@router.get("/{exp_id}/export/json")
def export_experiment_json(
    exp_id: str,
    db: Session = Depends(get_db),
):
    """Export experiment results as JSON."""
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    data = {
        "experiment_id": exp.id,
        "name": exp.name,
        "protocol": exp.protocol,
        "created_at": exp.created_at.isoformat(),
        "configuration": exp.configuration,
        "runs": [
            {
                "run_id": r.id,
                "status": r.status,
                "authentication_success": r.authentication_success,
                "session_key_match": r.session_key_match,
                "duration_ms": r.duration_ms,
                "message_count": r.message_count,
                "communication_bits": r.communication_bits,
                "created_at": r.created_at.isoformat(),
            }
            for r in exp.runs
        ],
    }

    content = json.dumps(data, indent=2)
    return StreamingResponse(
        io.StringIO(content),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=experiment_{exp_id}.json"},
    )


@router.get("/{exp_id}/export/csv")
def export_experiment_csv(
    exp_id: str,
    db: Session = Depends(get_db),
):
    """Export experiment results as CSV."""
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "run_id", "protocol", "status", "authentication_success",
            "session_key_match", "duration_ms", "message_count",
            "communication_bits", "created_at"
        ],
    )
    writer.writeheader()
    for r in exp.runs:
        writer.writerow({
            "run_id": r.id,
            "protocol": r.protocol,
            "status": r.status,
            "authentication_success": r.authentication_success,
            "session_key_match": r.session_key_match,
            "duration_ms": r.duration_ms,
            "message_count": r.message_count,
            "communication_bits": r.communication_bits,
            "created_at": r.created_at.isoformat(),
        })

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=experiment_{exp_id}.csv"},
    )
