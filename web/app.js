const assistantName = document.querySelector("#assistant-name");
const topicsContainer = document.querySelector("#topics");
const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const clearButton = document.querySelector("#clear-chat");
const sidebarPanel = document.querySelector("#sidebar-panel");
const toggleSidebarButton = document.querySelector("#toggle-sidebar");
let typingNode = null;
let lastContextQuestion = "";
const mobileMq = window.matchMedia("(max-width: 820px)");

function toSentenceCase(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function getTimeStamp() {
  return new Date().toLocaleTimeString("es-PE", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function addMessage(text, type = "bot", meta = "") {
  const message = document.createElement("div");
  message.className = `message ${type}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = type.includes("user") ? "Usuario" : "Asistente";

  const content = document.createElement("div");
  content.className = "message-content";
  content.textContent = toSentenceCase(text);

  const metaText = document.createElement("div");
  metaText.className = "message-meta";
  metaText.textContent = meta || getTimeStamp();
  content.appendChild(metaText);

  message.appendChild(avatar);
  message.appendChild(content);
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

function needsPreviousContext(text) {
  const normalized = String(text || "")
    .toLowerCase()
    .trim()
    .replace(/[^\p{L}\p{N}\s]/gu, "");
  if (!normalized) return false;

  const tokens = normalized.split(/\s+/).filter(Boolean);
  if (tokens.length <= 3) return true;

  const triggerWords = new Set(["si", "no", "entonces", "y", "ok", "vale"]);
  return tokens.some((token) => triggerWords.has(token));
}

function isTopicLikeQuestion(text) {
  const normalized = String(text || "").toLowerCase();
  const topicHints = [
    "aseo",
    "camion",
    "basura",
    "predial",
    "impuesto",
    "sisben",
    "hueco",
    "luminaria",
    "recoleccion",
    "cita",
  ];
  return topicHints.some((hint) => normalized.includes(hint));
}

function setBusy(isBusy) {
  questionInput.disabled = isBusy;
  form.querySelector("button").disabled = isBusy;
}

function setSidebarState(isOpen) {
  if (!sidebarPanel || !toggleSidebarButton) return;
  sidebarPanel.classList.toggle("is-open", isOpen);
  toggleSidebarButton.setAttribute("aria-expanded", String(isOpen));
  toggleSidebarButton.textContent = isOpen ? "Ocultar temas" : "Ver temas";
}

function syncSidebarByViewport() {
  if (!mobileMq.matches) {
    setSidebarState(true);
    return;
  }
  setSidebarState(false);
}

function showTyping() {
  if (typingNode) return;
  typingNode = document.createElement("div");
  typingNode.className = "message bot";
  typingNode.innerHTML = `
    <div class="message-avatar">Asistente</div>
    <div class="message-content">
      <span class="typing" aria-label="El asistente esta redactando una respuesta">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </span>
      <div class="message-meta">Redactando respuesta...</div>
    </div>
  `;
  messages.appendChild(typingNode);
  messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
  if (!typingNode) return;
  typingNode.remove();
  typingNode = null;
}

async function loadMenu() {
  const response = await fetch("/api/menu");
  const data = await response.json();

  assistantName.textContent = toSentenceCase(data.asistente);
  topicsContainer.innerHTML = "";

  data.temas.forEach((topic) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "topic-button";
    button.textContent = toSentenceCase(topic);
    button.addEventListener("click", () => {
      questionInput.value = toSentenceCase(topic);
      questionInput.focus();
      if (mobileMq.matches) {
        setSidebarState(false);
      }
    });
    topicsContainer.appendChild(button);
  });

  addMessage(data.bienvenida, "bot", "Mensaje de bienvenida");
}

async function sendQuestion(question) {
  const normalizedQuestion = toSentenceCase(question);
  const isContextDependent = needsPreviousContext(normalizedQuestion);
  const previousQuestion = lastContextQuestion || null;
  const isTopicQuestion = isTopicLikeQuestion(normalizedQuestion);
  if (isTopicQuestion || !lastContextQuestion) {
    lastContextQuestion = normalizedQuestion;
  }

  addMessage(normalizedQuestion, "user", getTimeStamp());
  setBusy(true);
  showTyping();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pregunta: normalizedQuestion,
        ultima_pregunta_usuario: previousQuestion || null,
      }),
    });

    if (!response.ok) {
      throw new Error("No fue posible procesar la consulta.");
    }

    const data = await response.json();
    hideTyping();
    addMessage(data.respuesta);
  } catch (error) {
    hideTyping();
    addMessage(error.message, "bot error");
  } finally {
    setBusy(false);
    questionInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  sendQuestion(question);
});

clearButton.addEventListener("click", () => {
  messages.innerHTML = "";
  lastContextQuestion = "";
  hideTyping();
  loadMenu();
});

if (toggleSidebarButton) {
  toggleSidebarButton.addEventListener("click", () => {
    const isOpen = sidebarPanel.classList.contains("is-open");
    setSidebarState(!isOpen);
  });
}

if (typeof mobileMq.addEventListener === "function") {
  mobileMq.addEventListener("change", syncSidebarByViewport);
} else if (typeof mobileMq.addListener === "function") {
  // Compatibilidad con navegadores moviles antiguos.
  mobileMq.addListener(syncSidebarByViewport);
}
syncSidebarByViewport();

loadMenu().catch(() => {
  addMessage("No fue posible cargar el menu inicial.", "bot error");
});
