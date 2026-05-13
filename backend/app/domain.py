from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ExerciseStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"


class Role(str, Enum):
    admin = "Admin"
    exercise_director = "Exercise Director"
    red_team_operator = "Red Team Operator"
    blue_team_analyst = "Blue Team Analyst"
    auditor = "Auditor"
    viewer = "Viewer"


class AttackTechnique(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str


class AttackMetadata(BaseModel):
    version: str
    techniques: list[AttackTechnique]


class ScenarioStep(BaseModel):
    id: str
    name: str
    target: str
    command: str
    expected_event_type: str
    expected_detection: str | None = None
    delay_seconds: int = 0


class ExpectedDetection(BaseModel):
    id: str
    name: str
    severity: str
    rule: str


class Scenario(BaseModel):
    id: str
    name: str
    version: str
    author: str
    last_updated: str
    difficulty: str
    execution_mode: str
    threat_actor_profile: str | None = None
    attack: AttackMetadata
    prerequisites: dict[str, Any]
    steps: list[ScenarioStep]
    expected_detections: list[ExpectedDetection]
    compliance: dict[str, list[str]]
    rollback: dict[str, str]


class ExerciseCreate(BaseModel):
    scenario_id: str
    requested_by: str = "local-operator"
    role: Role = Role.exercise_director


class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    requested_by: str
    status: ExerciseStatus = ExerciseStatus.queued
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status_reason: str | None = None


class TelemetryEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    exercise_id: str
    scenario_id: str
    step_id: str
    event_type: str
    target: str
    command: str
    message: str
    attack_techniques: list[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DetectionFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    exercise_id: str
    rule_id: str
    title: str
    severity: str
    event_id: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceArtifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    exercise_id: str
    name: str
    content_type: str
    sha256: str
    size_bytes: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    action: str
    resource: str
    outcome: str
    actor: str
    previous_hash: str
    hash: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Report(BaseModel):
    exercise: Exercise
    telemetry_count: int
    detection_count: int
    evidence_count: int
    attack_coverage: list[str]
    status: str
    recommendations: list[str]

