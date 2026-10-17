"""Pydantic schemas for security test and interactive playground endpoints."""

from __future__ import annotations

from typing import Any
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


# ---------------------------------------------------------------------------
# Interactive Security Playground Schemas
# ---------------------------------------------------------------------------

class PlaygroundLogEntry(BaseModel):
    timestamp_ms: float
    level: str  # "INFO", "ADVERSARY", "VERIFY", "DROP", "SUCCESS"
    node: str   # "User", "CloudServer", "ControlServer", "Adversary"
    message: str


class PlaygroundSamplePacketResponse(BaseModel):
    protocol: str
    message_name: str
    direction: str
    fields: dict[str, Any]
    field_descriptions: dict[str, str]
    available_presets: list[dict[str, str]]


class PlaygroundTamperRequest(BaseModel):
    protocol: str = Field(default="ju_park", description="Target protocol (ju_park, ecc, ml_kem)")
    attack_preset: str = Field(default="custom", description="Preset name or 'custom'")
    tamper_target_message: str = Field(default="M1", description="Message to tamper with (M1, M2, M3)")
    timestamp_offset_seconds: int = Field(default=0, description="Offset in seconds to add to timestamp (e.g. +60, -120)")
    field_to_tamper: str | None = Field(default=None, description="Specific field name to corrupt")
    tamper_action: str | None = Field(default=None, description="'flip_bit', 'random_noise', 'zero_out', 'custom_value', or 'none'")
    custom_tamper_value: str | None = Field(default=None, description="Custom value if tamper_action is 'custom_value'")
    simulate_replay: bool = Field(default=False, description="Simulate replay of previously consumed credentials")


class PlaygroundTamperResponse(BaseModel):
    protocol: str
    verdict: str  # "BLOCKED" (defense succeeded) or "ACCEPTED" (vulnerability/breach)
    is_blocked: bool
    stopped_at_stage: str
    dropped_by: str
    reason: str
    defense_explanation: str
    original_packet: dict[str, Any]
    tampered_packet: dict[str, Any]
    tampered_fields: list[str]
    logs: list[PlaygroundLogEntry]
    duration_ms: float


class FormalQuerySchema(BaseModel):
    query_id: str
    target: str
    query_type: str
    raw_query: str
    proved: bool
    status: str
    description: str


class SyntaxValidationSchema(BaseModel):
    valid: bool
    channels_found: list[str] = Field(default_factory=list)
    types_found: list[str] = Field(default_factory=list)
    events_found: list[str] = Field(default_factory=list)
    queries_found: list[str] = Field(default_factory=list)
    processes_found: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FormalVerificationSummarySchema(BaseModel):
    protocol_id: str
    protocol_name: str
    framework: str
    attacker_model: str
    security_level: str
    model_file: str
    has_binary: bool
    execution_source: str
    all_proved: bool
    theorems_count: int
    theorems_proved: int
    queries: list[FormalQuerySchema]
    syntax_validation: SyntaxValidationSchema
    features: list[str] = Field(default_factory=list)
    verification_time: float
    engine: str = "proverif"
    engine_name: str = "ProVerif"
    engine_version: str = "2.05+"


class FormalVerificationResponse(BaseModel):
    engine: str
    version: str
    has_binary: bool
    engine_id: str = "proverif"
    supported_engines: list[dict[str, Any]] = Field(default_factory=list)
    results: dict[str, FormalVerificationSummarySchema]


class FormalModelDetailResponse(BaseModel):
    protocol_id: str
    engine: str = "proverif"
    model_file: str
    source_code: str
    transcript: str

