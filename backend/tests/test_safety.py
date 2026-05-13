import pytest

from app.config import get_settings
from app.domain import ScenarioStep
from app.safety import SafetyError, validate_step_safety


def test_allows_configured_lab_host_and_command():
    step = ScenarioStep(
        id="step",
        name="safe",
        target="localhost",
        command="echo hello",
        expected_event_type="process",
    )

    validate_step_safety(step, get_settings().security)


def test_blocks_non_lab_target():
    step = ScenarioStep(
        id="step",
        name="unsafe-target",
        target="8.8.8.8",
        command="echo hello",
        expected_event_type="process",
    )

    with pytest.raises(SafetyError):
        validate_step_safety(step, get_settings().security)


def test_blocks_unsafe_command_pattern():
    step = ScenarioStep(
        id="step",
        name="unsafe-command",
        target="localhost",
        command="rm -rf /",
        expected_event_type="process",
    )

    with pytest.raises(SafetyError):
        validate_step_safety(step, get_settings().security)

