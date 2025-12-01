const API_BASE = "https://task-analyzer-l6sh.onrender.com";

const taskForm = document.getElementById("task-form");
const bulkJsonInput = document.getElementById("bulk-json");
const taskPreview = document.getElementById("task-preview");
const strategySelect = document.getElementById("strategy");
const analyzeBtn = document.getElementById("analyze-btn");
const statusBox = document.getElementById("status");
const resultsBox = document.getElementById("results");

let tasks = [];
let nextId = 1;

function showStatus(msg, type = "") {
  statusBox.textContent = msg || "";
  statusBox.className = "status " + (type ? type : "");
}

function refreshPreview() {
  taskPreview.textContent = JSON.stringify(tasks, null, 2);
}

taskForm.addEventListener("submit", (e) => {
  e.preventDefault();
  showStatus("");

  const title = document.getElementById("title").value.trim();
  const dueDateRaw = document.getElementById("due_date").value;
  const estimatedRaw = document.getElementById("estimated_hours").value;
  const importanceRaw = document.getElementById("importance").value;
  const depsRaw = document.getElementById("dependencies").value.trim();

  if (!title) {
    showStatus("Title is required.", "error");
    return;
  }

  const importance = parseInt(importanceRaw, 10);
  if (isNaN(importance) || importance < 1 || importance > 10) {
    showStatus("Importance must be between 1 and 10.", "error");
    return;
  }

  let estimated_hours = null;
  if (estimatedRaw !== "") {
    const eh = parseFloat(estimatedRaw);
    if (isNaN(eh) || eh < 0) {
      showStatus("Estimated hours must be a non-negative number.", "error");
      return;
    }
    estimated_hours = eh;
  }

  let dependencies = [];
  if (depsRaw) {
    dependencies = depsRaw
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s !== "")
      .map((s) => parseInt(s, 10))
      .filter((n) => !isNaN(n));
  }

  const task = {
    id: nextId++,
    title,
    due_date: dueDateRaw || null,
    estimated_hours,
    importance,
    dependencies,
  };

  tasks.push(task);
  refreshPreview();
  taskForm.reset();
  document.getElementById("importance").value = 5;
  showStatus("Task added to list.", "success");
});

analyzeBtn.addEventListener("click", async () => {
  showStatus("");
  resultsBox.innerHTML = "";

  let payload = [];

  if (bulkJsonInput.value.trim()) {
    try {
      payload = JSON.parse(bulkJsonInput.value.trim());
      if (!Array.isArray(payload)) {
        showStatus("Bulk JSON must be an array of tasks.", "error");
        return;
      }
    } catch (err) {
      showStatus("Invalid JSON in bulk input: " + err.message, "error");
      return;
    }
  } else {
    payload = tasks;
  }

  if (!payload || payload.length === 0) {
    showStatus("No tasks to analyze. Add tasks or paste JSON.", "error");
    return;
  }

  const strategy = strategySelect.value;

  try {
    showStatus("Analyzing tasks...", "success");

    const resp = await fetch(
      `${API_BASE}/api/tasks/analyze/?strategy=${encodeURIComponent(strategy)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    if (!resp.ok) {
      const text = await resp.text();
      showStatus(`API error (${resp.status}): ${text}`, "error");
      return;
    }

    const data = await resp.json();
    renderResults(data);
    showStatus(`Analysis complete. ${data.length} task(s) scored.`, "success");
  } catch (err) {
    console.error(err);
    showStatus("Network or server error: " + err.message, "error");
  }
});

function renderResults(tasks) {
  resultsBox.innerHTML = "";

  tasks.forEach((task) => {
    const div = document.createElement("div");
    div.className = "result-item";

    const header = document.createElement("div");
    header.className = "result-header";

    const titleEl = document.createElement("div");
    titleEl.textContent = task.title;

    const badge = document.createElement("span");
    badge.className = "badge";

    const score = task.score || 0;
    if (score >= 7) {
      badge.classList.add("badge-high");
      badge.textContent = `HIGH • ${score.toFixed(2)}`;
    } else if (score >= 4) {
      badge.classList.add("badge-medium");
      badge.textContent = `MEDIUM • ${score.toFixed(2)}`;
    } else {
      badge.classList.add("badge-low");
      badge.textContent = `LOW • ${score.toFixed(2)}`;
    }

    header.appendChild(titleEl);
    header.appendChild(badge);

    const meta = document.createElement("div");
    meta.className = "result-meta";

    const due = task.due_date || "None";
    const hrs =
      task.estimated_hours !== null && task.estimated_hours !== undefined
        ? task.estimated_hours
        : "N/A";

    meta.textContent = `Due: ${due} | Effort: ${hrs}h | Importance: ${
      task.importance ?? "N/A"
    }`;

    const expl = document.createElement("div");
    expl.className = "result-explanation";
    expl.textContent = task.explanation || "";

    div.appendChild(header);
    div.appendChild(meta);
    div.appendChild(expl);

    resultsBox.appendChild(div);
  });
}
