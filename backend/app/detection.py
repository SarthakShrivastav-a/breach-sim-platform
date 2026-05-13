from __future__ import annotations

from pathlib import Path

from app.config import load_yaml, repo_path
from app.domain import DetectionFinding, TelemetryEvent


class RuleStore:
    def __init__(self, rules_dir: Path | None = None) -> None:
        self.rules_dir = rules_dir or repo_path("rules")
        self.rules = self._load_rules()

    def _load_rules(self) -> list[dict]:
        rules: list[dict] = []
        for path in sorted(self.rules_dir.glob("*.yml")):
            rule = load_yaml(path)
            rule["_path"] = str(path)
            rules.append(rule)
        return rules

    def evaluate(self, event: TelemetryEvent) -> list[DetectionFinding]:
        findings: list[DetectionFinding] = []
        for rule in self.rules:
            selection = rule.get("detection", {}).get("selection", {})
            event_type = selection.get("event_type")
            command_contains = selection.get("command_contains", "")
            if event_type and event.event_type != event_type:
                continue
            if command_contains and command_contains.lower() not in event.command.lower():
                continue
            findings.append(
                DetectionFinding(
                    exercise_id=event.exercise_id,
                    rule_id=rule["id"],
                    title=rule["title"],
                    severity=rule["severity"],
                    event_id=event.id,
                    message=f"{rule['title']} matched telemetry event {event.id}",
                )
            )
        return findings

