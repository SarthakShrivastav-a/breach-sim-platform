import { useEffect, useMemo, useState } from "react";

import { fetchJson, summarizeExercise } from "./api.js";

const emptyState = {
  scenarios: [],
  exercises: [],
  detections: [],
  evidence: [],
  report: null,
  selectedExerciseId: null,
  error: ""
};

export default function App() {
  const [state, setState] = useState(emptyState);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try {
      const [scenarios, exercises] = await Promise.all([
        fetchJson("/api/scenarios"),
        fetchJson("/api/exercises")
      ]);
      setState((current) => ({ ...current, scenarios, exercises, error: "" }));
    } catch (error) {
      setState((current) => ({ ...current, error: error.message }));
    }
  }

  async function runScenario(scenarioId) {
    setLoading(true);
    try {
      const exercise = await fetchJson("/api/exercises", {
        method: "POST",
        body: JSON.stringify({
          scenario_id: scenarioId,
          requested_by: "frontend-operator",
          role: "Exercise Director"
        })
      });
      const [detections, evidence, report] = await Promise.all([
        fetchJson(`/api/exercises/${exercise.id}/detections`),
        fetchJson(`/api/exercises/${exercise.id}/evidence?role=Auditor`),
        fetchJson(`/api/exercises/${exercise.id}/report?role=Auditor`)
      ]);
      setState((current) => ({
        ...current,
        exercises: [exercise, ...current.exercises.filter((item) => item.id !== exercise.id)],
        selectedExerciseId: exercise.id,
        detections,
        evidence,
        report,
        error: ""
      }));
    } catch (error) {
      setState((current) => ({ ...current, error: error.message }));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const selectedExercise = useMemo(
    () => state.exercises.find((exercise) => exercise.id === state.selectedExerciseId),
    [state.exercises, state.selectedExerciseId]
  );
  const summary = selectedExercise
    ? summarizeExercise(selectedExercise, state.detections, state.evidence)
    : null;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Enterprise alpha</p>
          <h1>Breach Simulation Platform</h1>
        </div>
        <button type="button" onClick={refresh}>Refresh</button>
      </header>

      {state.error ? <section className="alert">{state.error}</section> : null}

      <section className="workspace">
        <aside className="panel">
          <h2>Scenario Library</h2>
          <div className="stack">
            {state.scenarios.map((scenario) => (
              <article className="scenario" key={scenario.id}>
                <div>
                  <strong>{scenario.name}</strong>
                  <span>{scenario.id} · ATT&CK {scenario.attack.version}</span>
                </div>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => runScenario(scenario.id)}
                >
                  Run
                </button>
              </article>
            ))}
          </div>
        </aside>

        <section className="panel">
          <h2>Active Exercise</h2>
          {summary ? (
            <div className="metrics">
              <div><span>Status</span><strong>{summary.status}</strong></div>
              <div><span>Detections</span><strong>{summary.detections}</strong></div>
              <div><span>Evidence</span><strong>{summary.evidence}</strong></div>
            </div>
          ) : (
            <p className="muted">Run a scenario to populate exercise telemetry.</p>
          )}

          <h3>Detections</h3>
          <div className="stack">
            {state.detections.map((finding) => (
              <article className="row" key={finding.id}>
                <strong>{finding.title}</strong>
                <span>{finding.severity}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <h2>After-Action Report</h2>
          {state.report ? (
            <>
              <div className="metrics">
                <div><span>Status</span><strong>{state.report.status}</strong></div>
                <div><span>Telemetry</span><strong>{state.report.telemetry_count}</strong></div>
                <div><span>Coverage</span><strong>{state.report.attack_coverage.join(", ")}</strong></div>
              </div>
              <ul>
                {state.report.recommendations.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </>
          ) : (
            <p className="muted">Reports appear after an exercise completes.</p>
          )}
        </section>
      </section>
    </main>
  );
}

