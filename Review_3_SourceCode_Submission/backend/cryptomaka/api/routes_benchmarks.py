"""Benchmark API routes."""

from __future__ import annotations

import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from cryptomaka.benchmarks.network_energy import (
    HARDWARE_PROFILES,
    NETWORK_PROFILES,
    simulate_all_protocols,
)
from cryptomaka.benchmarks.runner import run_benchmark, run_comparison_benchmark
from cryptomaka.database import BenchmarkResult, ProtocolRun, get_db
from cryptomaka.schemas.benchmarks import (
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    ComparisonRunRequest,
    HardwareProfileSchema,
    NetworkEnergyProfilesResponse,
    NetworkEnergySimulateRequest,
    NetworkEnergySimulateResponse,
    NetworkProfileSchema,
    ProtocolNetworkEnergySimulationSchema,
)

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/run", response_model=BenchmarkRunResponse)
def run_benchmark_endpoint(
    request: BenchmarkRunRequest,
    db: Session = Depends(get_db),
):
    """Run a benchmark for the specified protocol."""
    allowed = {"ju_park", "ecc", "reduced_roundtrip", "ml_kem"}
    if request.protocol not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown protocol '{request.protocol}'. Must be one of: {allowed}",
        )

    run_id = str(uuid.uuid4())

    try:
        result = run_benchmark(request.protocol, request.iterations, request.warmup)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Persist run record
    db_run = ProtocolRun(
        id=run_id,
        protocol=request.protocol,
        status="benchmark",
        authentication_success=False,
        session_key_match=False,
        implementation_version="0.1.0",
    )
    db.add(db_run)
    db.flush()

    # Persist benchmark result
    total = result["total"]
    db_bench = BenchmarkResult(
        run_id=run_id,
        protocol=request.protocol,
        iterations=total["iterations"],
        warmup_iterations=total["warmup_iterations"],
        mean_ms=total["mean_ms"],
        median_ms=total["median_ms"],
        min_ms=total["min_ms"],
        max_ms=total["max_ms"],
        stddev_ms=total["stddev_ms"],
        throughput_ops_per_sec=total["throughput_ops_per_sec"],
        communication_bits=result.get("communication_bits"),
        host_metadata=result.get("host_metadata"),
    )
    db.add(db_bench)
    db.commit()

    return BenchmarkRunResponse(
        run_id=run_id,
        protocol=request.protocol,
        iterations=request.iterations,
        warmup=request.warmup,
        total=total,
        registration=result["registration"],
        authentication=result["authentication"],
        communication_bits=result.get("communication_bits"),
        communication_report=result.get("communication_report"),
        host_metadata=result["host_metadata"],
    )


@router.post("/compare")
def compare_benchmarks(
    request: ComparisonRunRequest,
    db: Session = Depends(get_db),
):
    """Run benchmarks for multiple protocols and compare results."""
    allowed = {"ju_park", "ecc", "reduced_roundtrip", "ml_kem"}
    for p in request.protocols:
        if p not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown protocol '{p}'. Must be one of: {allowed}",
            )

    try:
        result = run_comparison_benchmark(request.protocols, request.iterations, request.warmup)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    metadata = result["host_metadata"]
    results = [
        {
            "protocol": protocol,
            "total": result["comparison"][protocol]["total"],
            "registration": result["comparison"][protocol]["registration"],
            "authentication": result["comparison"][protocol]["authentication"],
            "communication_bits": result["comparison"][protocol].get("communication_bits"),
            "communication_report": result["comparison"][protocol].get(
                "communication_report"
            ),
        }
        for protocol in request.protocols
    ]

    return {
        "comparison": result["comparison"],
        "results": results,
        "iterations": result["iterations"],
        "warmup": result["warmup"],
        "host_metadata": {
            "system": metadata.get("os", "unknown"),
            "machine": metadata.get("machine", "unknown"),
            "python_version": metadata.get("python_version", "unknown"),
            "os_release": metadata.get("os_release", "unknown"),
            "cpu": metadata.get("cpu", "unknown"),
        },
    }


@router.get("")
def list_benchmarks(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Return the most recent benchmark results."""
    results = (
        db.query(BenchmarkResult)
        .order_by(BenchmarkResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "run_id": r.run_id,
            "protocol": r.protocol,
            "iterations": r.iterations,
            "mean_ms": r.mean_ms,
            "median_ms": r.median_ms,
            "min_ms": r.min_ms,
            "max_ms": r.max_ms,
            "stddev_ms": r.stddev_ms,
            "throughput_ops_per_sec": r.throughput_ops_per_sec,
            "communication_bits": r.communication_bits,
            "created_at": r.created_at.isoformat(),
        }
        for r in results
    ]


@router.get("/network-energy/profiles", response_model=NetworkEnergyProfilesResponse)
def get_network_energy_profiles():
    """Return available wireless network channels and embedded hardware MCU profiles."""
    return NetworkEnergyProfilesResponse(
        network_profiles=[NetworkProfileSchema(**asdict(p)) for p in NETWORK_PROFILES.values()],
        hardware_profiles=[HardwareProfileSchema(**asdict(h)) for h in HARDWARE_PROFILES.values()],
    )


@router.post("/network-energy/simulate", response_model=NetworkEnergySimulateResponse)
def simulate_network_energy(request: NetworkEnergySimulateRequest):
    """Simulate transmission latency, MTU packet fragmentation, and microjoule energy consumption."""
    if request.network_profile not in NETWORK_PROFILES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown network profile '{request.network_profile}'. Available: {list(NETWORK_PROFILES.keys())}",
        )
    if request.hardware_profile not in HARDWARE_PROFILES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown hardware profile '{request.hardware_profile}'. Available: {list(HARDWARE_PROFILES.keys())}",
        )

    report = simulate_all_protocols(
        network_id=request.network_profile,
        hardware_id=request.hardware_profile,
        handshakes_per_day=request.handshakes_per_day,
        battery_capacity_mah=request.battery_capacity_mah,
    )

    return NetworkEnergySimulateResponse(
        network_profile=NetworkProfileSchema(**asdict(report.network_profile)),
        hardware_profile=HardwareProfileSchema(**asdict(report.hardware_profile)),
        battery_capacity_mah=report.battery_capacity_mah,
        handshakes_per_day=report.handshakes_per_day,
        results={
            k: ProtocolNetworkEnergySimulationSchema(**asdict(v))
            for k, v in report.results.items()
        },
    )

