from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.domain import Exercise, ExerciseCreate, Role
from app.engine import ScenarioEngine
from app.rbac import require_permission
from app.store import store


settings = get_settings()
engine = ScenarioEngine(store)

app = FastAPI(title=settings.app.name, version=settings.app.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def root_health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app.name, "version": settings.app.version}


@app.get(f"{settings.app.api_prefix}/health")
def api_health() -> dict[str, str]:
    return root_health()


@app.get(f"{settings.app.api_prefix}/scenarios")
def list_scenarios():
    return list(store.scenarios.values())


@app.get(f"{settings.app.api_prefix}/scenarios/{{scenario_id}}")
def get_scenario(scenario_id: str):
    scenario = store.scenarios.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@app.post(f"{settings.app.api_prefix}/exercises", status_code=201)
def create_exercise(payload: ExerciseCreate):
    require_permission(payload.role, "execute")
    if payload.scenario_id not in store.scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    exercise = store.add_exercise(
        Exercise(scenario_id=payload.scenario_id, requested_by=payload.requested_by)
    )
    return engine.run(exercise, store.scenarios[payload.scenario_id])


@app.get(f"{settings.app.api_prefix}/exercises")
def list_exercises(role: Role = Role.viewer):
    require_permission(role, "read")
    return list(store.exercises.values())


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}")
def get_exercise(exercise_id: str, role: Role = Role.viewer):
    require_permission(role, "read")
    if exercise_id not in store.exercises:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return store.exercises[exercise_id]


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}/telemetry")
def get_telemetry(exercise_id: str, role: Role = Role.viewer):
    require_permission(role, "read")
    return store.exercise_telemetry(exercise_id)


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}/detections")
def get_detections(exercise_id: str, role: Role = Role.viewer):
    require_permission(role, "read")
    return store.exercise_findings(exercise_id)


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}/evidence")
def get_evidence(exercise_id: str, role: Role = Role.auditor):
    require_permission(role, "audit")
    return store.exercise_evidence(exercise_id)


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}/report")
def get_report(exercise_id: str, role: Role = Role.auditor):
    require_permission(role, "audit")
    if exercise_id not in store.exercises:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return engine.report(exercise_id)


@app.get(f"{settings.app.api_prefix}/exercises/{{exercise_id}}/siem-export")
def export_siem(exercise_id: str, role: Role = Role.exercise_director):
    require_permission(role, "audit")
    if exercise_id not in store.exercises:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return engine.export_siem_events(exercise_id)


@app.get(f"{settings.app.api_prefix}/audit")
def get_audit(role: Role = Role.auditor):
    require_permission(role, "audit")
    return store.audit

