// Frontend for the AI Workspace.
// Rendering rule learned the hard way in ai_chatbot: NEVER put user input or
// model output into innerHTML — textContent can't be tricked into running
// scripts. All rendering below uses textContent.

const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");
const modelSelect = document.getElementById("modelSelect");
const summarizeInput = document.getElementById("summarizeInput");
const summarizeBtn = document.getElementById("summarizeBtn");
const summarizeResult = document.getElementById("summarizeResult");

// The conversation so far, in the same shape the backend expects.
// The server is stateless (until Milestone 2 adds a database), so the
// browser owns the history and sends all of it with every request.
const messages = [];

// ---------- tabs ----------

for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => {
    document.querySelector(".tab.active").classList.remove("active");
    document.querySelector(".panel.active").classList.remove("active");
    tab.classList.add("active");
    document.getElementById(tab.dataset.panel).classList.add("active");
  });
}

// ---------- model picker ----------

async function loadModels() {
  try {
    const res = await fetch("/api/models");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    for (const m of data.models) {
      const option = document.createElement("option");
      option.value = m.name;
      option.textContent = m.parameter_size
        ? `${m.name} (${m.parameter_size})`
        : m.name;
      modelSelect.appendChild(option);
    }
  } catch (err) {
    console.error("Could not load models:", err);
    // Leave the picker empty; the backend falls back to its default model.
  }
}

// Selected model, or null to let the backend use its configured default.
function selectedModel() {
  return modelSelect.value || null;
}

// ---------- chat ----------

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault(); // stay on the page instead of reloading it
  const text = chatInput.value.trim();
  if (!text || chatSend.disabled) return;

  chatSend.disabled = true;
  chatInput.value = "";
  addMessage("user", text);
  messages.push({ role: "user", content: text });

  try {
    await streamReply();
  } finally {
    chatSend.disabled = false;
    chatInput.focus();
  }
});

async function streamReply() {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, model: selectedModel() }),
  });

  if (!res.ok) {
    // Validation errors (422) etc. arrive as normal JSON, not a stream.
    const data = await res.json().catch(() => null);
    addMessage("error", data?.detail?.toString() ?? `Request failed (HTTP ${res.status})`);
    return;
  }

  // Read the SSE stream: events are "data: {...}" blocks separated by a
  // blank line. The reader hands us raw bytes; we buffer until we have at
  // least one complete event, then process it.
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  const bubble = addMessage("assistant", "");
  let buffer = "";
  let reply = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop(); // last piece may be incomplete — keep for next round

    for (const event of events) {
      const dataLine = event.split("\n").find((l) => l.startsWith("data: "));
      if (!dataLine) continue;
      const data = JSON.parse(dataLine.slice("data: ".length));

      if (data.token) {
        reply += data.token;
        bubble.textContent = reply;
        chatLog.scrollTop = chatLog.scrollHeight;
      } else if (data.error) {
        bubble.remove();
        addMessage("error", data.error);
        return;
      }
      // data.done needs no handling: the loop ends when the stream closes.
    }
  }

  if (reply) {
    // Remember the assistant's answer so the next request has full context.
    messages.push({ role: "assistant", content: reply });
  }
}

// ---------- summarize ----------

summarizeBtn.addEventListener("click", async () => {
  const text = summarizeInput.value.trim();
  if (!text || summarizeBtn.disabled) return;

  summarizeBtn.disabled = true;
  summarizeResult.hidden = false;
  summarizeResult.classList.remove("error");
  summarizeResult.textContent = "Summarizing…";

  try {
    const res = await fetch("/api/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model: selectedModel() }),
    });
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      summarizeResult.classList.add("error");
      summarizeResult.textContent =
        data?.detail?.toString() ?? `Request failed (HTTP ${res.status})`;
      return;
    }
    summarizeResult.textContent = data.summary;
  } catch (err) {
    console.error("Error:", err);
    summarizeResult.classList.add("error");
    summarizeResult.textContent = "Network error — is the server running?";
  } finally {
    summarizeBtn.disabled = false;
  }
});

loadModels();
