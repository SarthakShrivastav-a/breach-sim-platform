from __future__ import annotations

from fastapi import HTTPException, status

from app.domain import Role


PERMISSIONS: dict[str, set[str]] = {
    Role.admin.value: {"read", "execute", "audit", "configure"},
    Role.exercise_director.value: {"read", "execute", "audit"},
    Role.red_team_operator.value: {"read", "execute"},
    Role.blue_team_analyst.value: {"read", "audit"},
    Role.auditor.value: {"read", "audit"},
    Role.viewer.value: {"read"},
}


def require_permission(role: Role, permission: str) -> None:
    if permission not in PERMISSIONS.get(role.value, set()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{role.value} cannot perform {permission}",
        )

