import assert from "node:assert/strict";
import test from "node:test";

import { summarizeExercise } from "./api.js";

test("summarizeExercise returns stable dashboard fields", () => {
  const summary = summarizeExercise(
    { id: "ex-1", status: "completed", completed_at: "2026-05-13T00:00:00Z" },
    [{ id: "det-1" }],
    [{ id: "ev-1" }, { id: "ev-2" }]
  );

  assert.deepEqual(summary, {
    id: "ex-1",
    status: "completed",
    detections: 1,
    evidence: 2,
    completed: true
  });
});

