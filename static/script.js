const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});

function addMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);
  messageDiv.textContent = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const userText = input.value.trim();
  if (!userText) return;

  addMessage(userText, "user");
  input.value = "";

  // Show placeholder while waiting for response
  addMessage("Generating itinerary... please wait ⏳", "bot");

  fetch("/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: userText }),
  })
    .then((res) => res.json())
    .then((data) => {
      const botMessages = document.querySelectorAll(".bot");
      const lastBot = botMessages[botMessages.length - 1];

      lastBot.textContent = data.response || "❌ Failed to get response from server.";
    })
    .catch((err) => {
      const botMessages = document.querySelectorAll(".bot");
      const lastBot = botMessages[botMessages.length - 1];
      lastBot.textContent = "❌ Error connecting to server.";
      console.error(err);
    });
}
