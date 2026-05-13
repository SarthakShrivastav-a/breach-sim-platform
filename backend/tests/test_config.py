from app.config import get_settings


def test_settings_load_from_yaml():
    settings = get_settings()

    assert settings.app.name == "Breach Simulation Platform"
    assert settings.security.attack_version == "19.0"
    assert "echo" in settings.security.allowed_commands

