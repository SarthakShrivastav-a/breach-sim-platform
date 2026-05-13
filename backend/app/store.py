from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.config import load_yaml, repo_path
from app.domain import (
    AuditRecord,
    DetectionFinding,
    EvidenceArtifact,
    Exercise,
    Scenario,
    TelemetryEvent,
)


class PlatformStore:
    def __init__(self, scenarios_dir: Path | None = None) -> None:
        self.scenarios_dir = scenarios_dir or repo_path("scenarios")
        self.scenarios = self._load_scenarios()
        self.exercises: dict[str, Exercise] = {}
        self.telemetry: list[TelemetryEvent] = []
        self.findings: list[DetectionFinding] = []
        self.evidence: list[EvidenceArtifact] = []
        self.audit: list[AuditRecord] = []

    def _load_scenarios(self) -> dict[str, Scenario]:
        scenarios: dict[str, Scenario] = {}
        for path in sorted(self.scenarios_dir.glob("*.yaml")):
            scenario = Scenario.model_validate(load_yaml(path))
            scenarios[scenario.id] = scenario
        return scenarios

    def add_exercise(self, exercise: Exercise) -> Exercise:
        self.exercises[exercise.id] = exercise
        self.audit_action("exercise.created", exercise.id, "success", exercise.requested_by)
        return exercise

    def add_telemetry(self, event: TelemetryEvent) -> TelemetryEvent:
        self.telemetry.append(event)
        self.audit_action("telemetry.recorded", event.id, "success", "system")
        return event

    def add_findings(self, findings: list[DetectionFinding]) -> list[DetectionFinding]:
        self.findings.extend(findings)
        for finding in findings:
            self.audit_action("detection.created", finding.id, "success", "system")
        return findings

    def add_evidence(self, exercise_id: str, name: str, content: bytes) -> EvidenceArtifact:
        artifact = EvidenceArtifact(
            exercise_id=exercise_id,
            name=name,
            content_type="application/json",
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
        )
        self.evidence.append(artifact)
        self.audit_action("evidence.created", artifact.id, "success", "system")
        return artifact

    def audit_action(self, action: str, resource: str, outcome: str, actor: str) -> AuditRecord:
        previous_hash = self.audit[-1].hash if self.audit else "0" * 64
        payload = {
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "actor": actor,
            "previous_hash": previous_hash,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        record = AuditRecord(
            action=action,
            resource=resource,
            outcome=outcome,
            actor=actor,
            previous_hash=previous_hash,
            hash=digest,
        )
        self.audit.append(record)
        return record

    def exercise_telemetry(self, exercise_id: str) -> list[TelemetryEvent]:
        return [event for event in self.telemetry if event.exercise_id == exercise_id]

    def exercise_findings(self, exercise_id: str) -> list[DetectionFinding]:
        return [finding for finding in self.findings if finding.exercise_id == exercise_id]

    def exercise_evidence(self, exercise_id: str) -> list[EvidenceArtifact]:
        return [artifact for artifact in self.evidence if artifact.exercise_id == exercise_id]


store = PlatformStore()

