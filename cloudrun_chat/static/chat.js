const form = document.querySelector("#chat-form");
const promptInput = document.querySelector("#prompt");
const promptCount = document.querySelector("#prompt-count");
const submitButton = form.querySelector("button");
const messages = document.querySelector("#messages");
const quickButtons = document.querySelectorAll("[data-prompt]");
const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const promptMaxLength = Number(promptInput.dataset.maxLength || promptInput.maxLength);
const HEALTH_POLL_INTERVAL_MS = 30000;
const HEALTH_REQUEST_TIMEOUT_MS = 8000;
const QUERY_REQUEST_TIMEOUT_MS = 25000;
let isSubmitting = false;
let isRefreshingHealth = false;
let hasLoadedHealth = false;
let healthPollId = null;
let currentStatusState = "pending";
let currentStatusSource = "health";

function updateSubmitState() {
  const hasPrompt = promptInput.value.trim().length > 0;
  submitButton.disabled = isSubmitting || !hasPrompt;
}

function addMessage(role, html) {
  const node = document.createElement("div");
  node.className = `message message--${role}`;
  node.innerHTML = html;
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
  return node;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function updatePromptCount() {
  if (!promptCount || !Number.isFinite(promptMaxLength) || promptMaxLength <= 0) {
    updateSubmitState();
    return;
  }
  const remaining = Math.max(0, promptMaxLength - promptInput.value.length);
  promptCount.textContent = `${remaining} left`;
  updateSubmitState();
}

function renderTable(rows) {
  if (!rows.length) {
    return "";
  }

  const columns = Object.keys(rows[0]);
  const head = columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = columns.map((column) => `<td>${escapeHtml(row[column])}</td>`).join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${head}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

async function parseJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return {
      error: `The chat service returned ${response.status} instead of JSON.`,
    };
  }
  return response.json();
}

async function fetchWithTimeout(url, options = {}, timeoutMs = QUERY_REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(`Request timed out after ${Math.round(timeoutMs / 1000)}s.`);
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

function setServiceStatus(state, text, { source = "health", preserveQueryError = false } = {}) {
  if (!statusDot || !statusText) {
    return;
  }

  if (preserveQueryError && currentStatusSource === "query" && currentStatusState === "error") {
    return;
  }

  currentStatusState = state;
  currentStatusSource = source;
  statusDot.className = `status-dot status-dot--${state}`;
  statusText.textContent = text;
}

async function refreshHealth({ showPending = false } = {}) {
  if (isSubmitting || isRefreshingHealth) {
    return;
  }

  isRefreshingHealth = true;
  if (showPending || !hasLoadedHealth) {
    setServiceStatus("pending", "Checking service");
  }

  try {
    const response = await fetchWithTimeout("/health", {
      headers: { Accept: "application/json" },
    }, HEALTH_REQUEST_TIMEOUT_MS);
    const payload = await parseJsonResponse(response);

    if (!response.ok || payload.status !== "ok") {
      throw new Error(payload.error || "Health probe failed");
    }

    hasLoadedHealth = true;
    setServiceStatus("healthy", `Healthy: ${payload.dataset}`, {
      preserveQueryError: true,
    });
  } catch (error) {
    setServiceStatus("error", error.message || "Service unavailable");
  } finally {
    isRefreshingHealth = false;
  }
}

async function submitPrompt(prompt, intent = "") {
  const trimmed = prompt.trim();
  if (!trimmed || isSubmitting) {
    updateSubmitState();
    return;
  }

  isSubmitting = true;
  promptInput.disabled = true;
  updateSubmitState();
  messages.setAttribute("aria-busy", "true");
  quickButtons.forEach((button) => {
    button.disabled = true;
  });

  addMessage("user", `<p>${escapeHtml(trimmed)}</p>`);
  promptInput.value = "";
  updatePromptCount();
  const loading = addMessage("bot", "<p>Searching BigQuery marts...</p>");

  try {
    const response = await fetchWithTimeout("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: trimmed, intent }),
    }, QUERY_REQUEST_TIMEOUT_MS);
    const payload = await parseJsonResponse(response);

    if (!response.ok) {
      promptInput.value = trimmed;
      updatePromptCount();
      setServiceStatus("error", "Last query failed", { source: "query" });
      loading.innerHTML = `<p>${escapeHtml(payload.error || "The query could not be routed.")}</p>`;
      return;
    }

    setServiceStatus(
      "healthy",
      `Healthy: ${payload.row_count} row${payload.row_count === 1 ? "" : "s"}`,
      { source: "query" },
    );
    loading.innerHTML = `
      <p><strong>${escapeHtml(payload.title)}</strong></p>
      <p>${escapeHtml(payload.answer)}</p>
      <p class="message-meta">${escapeHtml(`${payload.row_count} row${payload.row_count === 1 ? "" : "s"} returned`)}</p>
      ${renderTable(payload.rows || [])}
    `;
  } catch (error) {
    promptInput.value = trimmed;
    updatePromptCount();
    const message = error.message || "Unable to reach the chat service.";
    setServiceStatus("error", message, { source: "query" });
    loading.innerHTML = `<p>${escapeHtml(message)}</p><p>Check the local server or Cloud Run deployment.</p>`;
  } finally {
    isSubmitting = false;
    promptInput.disabled = false;
    updateSubmitState();
    messages.setAttribute("aria-busy", "false");
    quickButtons.forEach((button) => {
      button.disabled = false;
    });
    promptInput.focus();
  }
}

function startHealthPolling() {
  if (healthPollId !== null) {
    return;
  }

  healthPollId = window.setInterval(() => {
    if (!document.hidden) {
      refreshHealth();
    }
  }, HEALTH_POLL_INTERVAL_MS);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitPrompt(promptInput.value);
});

promptInput.addEventListener("input", updatePromptCount);
updatePromptCount();
refreshHealth({ showPending: true });
startHealthPolling();

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    refreshHealth();
  }
});

quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    submitPrompt(button.dataset.prompt, button.dataset.intent || "");
  });
});
