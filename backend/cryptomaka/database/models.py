"""
SQLAlchemy ORM models for CryptoMAKA Lab.

IMPORTANT: No secrets, passwords, session keys, or biometric data are stored.
All sensitive material is deliberately excluded from persistence.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cryptomaka.database.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Experiment(Base):
    """Top-level experiment container."""

    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    protocol: Mapped[str] = mapped_column(String(50), nullable=False)
    configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    # Relationships
    runs: Mapped[list[ProtocolRun]] = relationship(
        "ProtocolRun", back_populates="experiment", cascade="all, delete-orphan"
    )


class ProtocolRun(Base):
    """Single protocol execution record."""

    __tablename__ = "protocol_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    experiment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="SET NULL"), nullable=True
    )
    protocol: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success / error
    authentication_success: Mapped[bool] = mapped_column(Boolean, default=False)
    session_key_match: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    message_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    communication_bits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    implementation_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    messages_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    # Relationships
    experiment: Mapped[Experiment | None] = relationship("Experiment", back_populates="runs")
    security_results: Mapped[list[SecurityTestResult]] = relationship(
        "SecurityTestResult", back_populates="run", cascade="all, delete-orphan"
    )
    benchmark_results: Mapped[list[BenchmarkResult]] = relationship(
        "BenchmarkResult", back_populates="run", cascade="all, delete-orphan"
    )


class SecurityTestResult(Base):
    """Result of a single security test against a protocol run."""

    __tablename__ = "security_test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("protocol_runs.id", ondelete="SET NULL"), nullable=True
    )
    test_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)  # PASS / FAIL
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    run: Mapped[ProtocolRun | None] = relationship(
        "ProtocolRun", back_populates="security_results"
    )


class BenchmarkResult(Base):
    """Statistical benchmark metrics for a protocol."""

    __tablename__ = "benchmark_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("protocol_runs.id", ondelete="SET NULL"), nullable=True
    )
    protocol: Mapped[str] = mapped_column(String(50), nullable=False)
    iterations: Mapped[int] = mapped_column(Integer, nullable=False)
    warmup_iterations: Mapped[int] = mapped_column(Integer, default=0)
    mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    min_ms: Mapped[float] = mapped_column(Float, nullable=False)
    max_ms: Mapped[float] = mapped_column(Float, nullable=False)
    stddev_ms: Mapped[float] = mapped_column(Float, nullable=False)
    throughput_ops_per_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_bits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    host_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    run: Mapped[ProtocolRun | None] = relationship(
        "ProtocolRun", back_populates="benchmark_results"
    )


class SystemMetadata(Base):
    """Stored environment metadata for reproducibility."""

    __tablename__ = "system_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    python_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    os_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cpu_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
