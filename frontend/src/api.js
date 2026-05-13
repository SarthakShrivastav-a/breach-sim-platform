const API_BASE = import.meta.env?.VITE_API_BASE_URL || "";

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export function summarizeExercise(exercise, detections = [], evidence = []) {
  return {
    id: exercise.id,
    status: exercise.status,
    detections: detections.length,
    evidence: evidence.length,
    completed: Boolean(exercise.completed_at)
  };
}
