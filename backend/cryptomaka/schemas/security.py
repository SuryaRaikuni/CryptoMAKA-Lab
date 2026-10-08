"""Pydantic schemas for security test endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SecurityTestResultSchema(BaseModel):
    test: str
    status: str  # "PASS" or "FAIL"
    description: str
    evidence: str
    severity: str
    duration_ms: float


class SecurityRunRequest(BaseModel):
    protocol: str = Field(default="ju_park", description="Protocol to test")


class SecurityRunResponse(BaseModel):
    run_id: str
    protocol: str
    total: int
    passed: int
    failed: int
    disclaimer: str
    results: list[SecurityTestResultSchema]
