from __future__ import annotations

import ipaddress
import shlex

from app.config import SecurityConfig
from app.domain import ScenarioStep


class SafetyError(ValueError):
    pass


def validate_step_safety(step: ScenarioStep, security: SecurityConfig) -> None:
    _validate_target(step.target, security)
    _validate_command(step.command, security)


def _validate_target(target: str, security: SecurityConfig) -> None:
    if target in security.allowed_lab_hosts:
        return
    try:
        ip = ipaddress.ip_address(target)
    except ValueError as exc:
        raise SafetyError(f"Target {target!r} is not an allowed lab host") from exc
    for cidr in security.allowed_lab_cidrs:
        if ip in ipaddress.ip_network(cidr):
            return
    raise SafetyError(f"Target {target!r} is outside allowed lab CIDRs")


def _validate_command(command: str, security: SecurityConfig) -> None:
    lowered = command.lower()
    for blocked in security.blocked_command_patterns:
        if blocked.lower() in lowered:
            raise SafetyError(f"Command contains blocked pattern {blocked!r}")
    try:
        first_token = shlex.split(command, posix=False)[0]
    except (ValueError, IndexError) as exc:
        raise SafetyError("Command is empty or cannot be parsed") from exc
    normalized = first_token.lower().removesuffix(".exe")
    allowed = {item.lower() for item in security.allowed_commands}
    if normalized not in allowed:
        raise SafetyError(f"Command {first_token!r} is not allowlisted")

