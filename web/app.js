const assistantName = document.querySelector("#assistant-name");
const topicsContainer = document.querySelector("#topics");
const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const clearButton = document.querySelector("#clear-chat");

function addMessage(text, type = "bot") {
  const message = document.createElement("div");
  message.className = `message ${type}`;
  message.textContent = text;
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

function setBusy(isBusy) {
  questionInput.disabled = isBusy;
  form.querySelector("button").disabled = isBusy;
}

async function loadMenu() {
  const response = await fetch("/api/menu");
  const data = await response.json();

  assistantName.textContent = data.asistente;
  topicsContainer.innerHTML = "";

  data.temas.forEach((topic) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "topic-button";
    button.textContent = topic;
    button.addEventListener("click", () => {
      questionInput.value = topic;
      questionInput.focus();
    });
    topicsContainer.appendChild(button);
  });

  addMessage(data.bienvenida);
}

async function sendQuestion(question) {
  addMessage(question, "user");
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ pregunta: question }),
    });

    if (!response.ok) {
      throw new Error("No fue posible procesar la consulta.");
    }

    const data = await response.json();
    addMessage(data.respuesta);
  } catch (error) {
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
  loadMenu();
});

loadMenu().catch(() => {
  addMessage("No fue posible cargar el menu inicial.", "bot error");
});
