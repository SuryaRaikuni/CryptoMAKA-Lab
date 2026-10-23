"""Pydantic schemas for protocol API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MessageMetadata(BaseModel):
    name: str
    direction: str
    size_bits: int


class ProtocolTimings(BaseModel):
    registration_ms: float = 0.0
    authentication_ms: float = 0.0
    key_derivation_ms: float = 0.0
    total_ms: float = 0.0


class ProtocolRunRequest(BaseModel):
    protocol: str = Field(..., description="Protocol name: ju_park, ecc, or reduced_roundtrip")


class ProtocolRunResponse(BaseModel):
    run_id: str
    protocol: str
    status: str
    participants: int
    authentication_success: bool
    session_key_match: bool
    message_count: int
    messages: list[MessageMetadata]
    timings: dict[str, float]
    communication_bits: Optional[int] = None
    notes: list[str] = Field(default_factory=list)


class ProtocolInfo(BaseModel):
    id: str
    name: str
    description: str
    message_count: int
    primitives: list[str]
    label: str  # "published", "ecc_counterpart", "proposed_extension"
