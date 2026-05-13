from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "app.yaml"


class AppConfig(BaseModel):
    name: str
    version: str
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=list)


class DatabaseConfig(BaseModel):
    url_env: str
    default_url: str

    @property
    def url(self) -> str:
        return os.getenv(self.url_env, self.default_url)


class RedisConfig(BaseModel):
    url_env: str
    default_url: str

    @property
    def url(self) -> str:
        return os.getenv(self.url_env, self.default_url)


class SecurityConfig(BaseModel):
    attack_version: str
    default_execution_mode: str
    allowed_commands: list[str]
    allowed_lab_hosts: list[str]
    allowed_lab_cidrs: list[str]
    blocked_command_patterns: list[str]


class IntegrationEndpointConfig(BaseModel):
    enabled: bool = False
    hec_url_env: str | None = None
    token_env: str | None = None
    workspace_id_env: str | None = None
    shared_key_env: str | None = None
    leef_endpoint_env: str | None = None
    url_env: str | None = None


class IntegrationsConfig(BaseModel):
    splunk: IntegrationEndpointConfig
    sentinel: IntegrationEndpointConfig
    qradar: IntegrationEndpointConfig
    webhook: IntegrationEndpointConfig


class DockerConfig(BaseModel):
    image_repository: str
    publish_enabled_env: str

    @property
    def publish_enabled(self) -> bool:
        return os.getenv(self.publish_enabled_env, "false").lower() == "true"


class Settings(BaseModel):
    app: AppConfig
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    integrations: IntegrationsConfig
    docker: DockerConfig


@lru_cache
def get_settings(config_path: str | None = None) -> Settings:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Settings.model_validate(raw)


def repo_path(*parts: str) -> Path:
    return ROOT_DIR.joinpath(*parts)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

