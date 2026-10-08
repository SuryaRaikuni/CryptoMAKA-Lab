"""Pydantic schemas for experiment endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExperimentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    protocol: str = Field(..., description="Protocol: ju_park, ecc, or reduced_roundtrip")
    configuration: Optional[dict[str, Any]] = None
    run_benchmark: bool = Field(default=False)
    run_security: bool = Field(default=False)
    benchmark_iterations: int = Field(default=50, ge=1, le=5000)


class ExperimentSummary(BaseModel):
    id: str
    name: str
    protocol: str
    created_at: datetime
    run_count: int = 0


class ExperimentDetail(ExperimentSummary):
    configuration: Optional[dict[str, Any]] = None
    runs: list[dict[str, Any]] = Field(default_factory=list)
