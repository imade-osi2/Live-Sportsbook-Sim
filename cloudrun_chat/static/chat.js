const form = document.querySelector("#chat-form");
const promptInput = document.querySelector("#prompt");
const submitButton = form.querySelector("button");
const messages = document.querySelector("#messages");
const quickButtons = document.querySelectorAll("[data-prompt]");
let isSubmitting = false;

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

async function submitPrompt(prompt) {
  const trimmed = prompt.trim();
  if (!trimmed || isSubmitting) {
    return;
  }

  isSubmitting = true;
  promptInput.disabled = true;
  submitButton.disabled = true;
  messages.setAttribute("aria-busy", "true");
  quickButtons.forEach((button) => {
    button.disabled = true;
  });

  addMessage("user", `<p>${escapeHtml(trimmed)}</p>`);
  promptInput.value = "";
  const loading = addMessage("bot", "<p>Searching BigQuery marts...</p>");

  try {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: trimmed }),
    });
    const payload = await parseJsonResponse(response);

    if (!response.ok) {
      loading.innerHTML = `<p>${escapeHtml(payload.error || "The query could not be routed.")}</p>`;
      return;
    }

    loading.innerHTML = `
      <p><strong>${escapeHtml(payload.title)}</strong></p>
      <p>${escapeHtml(payload.answer)}</p>
      ${renderTable(payload.rows || [])}
    `;
  } catch (error) {
    loading.innerHTML = "<p>Unable to reach the chat service. Check the local server or Cloud Run deployment.</p>";
  } finally {
    isSubmitting = false;
    promptInput.disabled = false;
    submitButton.disabled = false;
    messages.setAttribute("aria-busy", "false");
    quickButtons.forEach((button) => {
      button.disabled = false;
    });
    promptInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitPrompt(promptInput.value);
});

quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    submitPrompt(button.dataset.prompt);
  });
});
