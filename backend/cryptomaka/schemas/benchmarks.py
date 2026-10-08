"""Pydantic schemas for benchmark endpoints."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class BenchmarkRunRequest(BaseModel):
    protocol: str = Field(..., description="Protocol: ju_park, ecc, or reduced_roundtrip")
    iterations: int = Field(default=100, ge=1, le=10000)
    warmup: int = Field(default=10, ge=0, le=100)


class BenchmarkMetricsSchema(BaseModel):
    iterations: int
    warmup_iterations: int
    mean_ms: float
    median_ms: float
    min_ms: float
    max_ms: float
    stddev_ms: float
    throughput_ops_per_sec: float


class BenchmarkRunResponse(BaseModel):
    run_id: str
    protocol: str
    iterations: int
    warmup: int
    total: BenchmarkMetricsSchema
    registration: BenchmarkMetricsSchema
    authentication: BenchmarkMetricsSchema
    communication_bits: Optional[int] = None
    communication_report: Optional[dict[str, Any]] = None
    host_metadata: dict[str, Any]


class ComparisonRunRequest(BaseModel):
    protocols: list[str] = Field(
        default=["ju_park", "ecc", "reduced_roundtrip"]
    )
    iterations: int = Field(default=50, ge=1, le=5000)
    warmup: int = Field(default=10, ge=0, le=100)
