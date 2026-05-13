from __future__ import annotations

import json
from datetime import UTC, datetime

from app.config import get_settings
from app.detection import RuleStore
from app.domain import Exercise, ExerciseStatus, Report, Scenario, TelemetryEvent
from app.safety import SafetyError, validate_step_safety
from app.store import PlatformStore


class ScenarioEngine:
    def __init__(self, store: PlatformStore, rules: RuleStore | None = None) -> None:
        self.store = store
        self.rules = rules or RuleStore()

    def run(self, exercise: Exercise, scenario: Scenario) -> Exercise:
        settings = get_settings()
        exercise.status = ExerciseStatus.running
        exercise.started_at = datetime.now(UTC)
        try:
            for step in scenario.steps:
                validate_step_safety(step, settings.security)
                event = TelemetryEvent(
                    exercise_id=exercise.id,
                    scenario_id=scenario.id,
                    step_id=step.id,
                    event_type=step.expected_event_type,
                    target=step.target,
                    command=step.command,
                    message=f"Alpha simulation executed {step.name}",
                    attack_techniques=[
                        technique.technique_id for technique in scenario.attack.techniques
                    ],
                )
                self.store.add_telemetry(event)
                self.store.add_findings(self.rules.evaluate(event))
            report = self.report(exercise.id)
            self.store.add_evidence(
                exercise.id,
                "after-action-report.json",
                report.model_dump_json().encode("utf-8"),
            )
            exercise.status = ExerciseStatus.completed
            exercise.completed_at = datetime.now(UTC)
        except SafetyError as exc:
            exercise.status = ExerciseStatus.blocked
            exercise.status_reason = str(exc)
            exercise.completed_at = datetime.now(UTC)
            self.store.audit_action("exercise.blocked", exercise.id, "blocked", "safety")
        except Exception as exc:
            exercise.status = ExerciseStatus.failed
            exercise.status_reason = str(exc)
            exercise.completed_at = datetime.now(UTC)
            self.store.audit_action("exercise.failed", exercise.id, "failed", "system")
            raise
        return exercise

    def report(self, exercise_id: str) -> Report:
        exercise = self.store.exercises[exercise_id]
        scenario = self.store.scenarios[exercise.scenario_id]
        telemetry = self.store.exercise_telemetry(exercise_id)
        findings = self.store.exercise_findings(exercise_id)
        evidence = self.store.exercise_evidence(exercise_id)
        expected = {item.id for item in scenario.expected_detections}
        actual = {item.rule_id for item in findings}
        missing = sorted(expected - actual)
        recommendations = (
            ["All expected alpha detections fired."]
            if not missing
            else [f"Investigate missing expected detections: {', '.join(missing)}"]
        )
        return Report(
            exercise=exercise,
            telemetry_count=len(telemetry),
            detection_count=len(findings),
            evidence_count=len(evidence),
            attack_coverage=[item.technique_id for item in scenario.attack.techniques],
            status="passed" if not missing else "needs-review",
            recommendations=recommendations,
        )

    def export_siem_events(self, exercise_id: str) -> dict[str, list[dict]]:
        telemetry = self.store.exercise_telemetry(exercise_id)
        return {
            "splunk_hec": [
                {"event": event.model_dump(mode="json"), "sourcetype": "breach:simulation"}
                for event in telemetry
            ],
            "qradar_leef": [
                {
                    "leef": (
                        "LEEF:2.0|BreachSimulation|CyberRange|1.0|"
                        f"{event.event_type}|devTime={event.timestamp.isoformat()}"
                    )
                }
                for event in telemetry
            ],
            "sentinel_json": [json.loads(event.model_dump_json()) for event in telemetry],
        }

