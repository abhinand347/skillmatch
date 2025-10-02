const chat = document.getElementById("chat");
const input = document.getElementById("userInput");
const home = document.getElementById("home");
const chatUI = document.getElementById("chatUI");
let mode = "chatty";

// Keep a session ID per mode
let sessionIds = { chatty: null, compact: null };

const chattyGreetings = [
  "Let's see what you're made of! 💪 Drop your skills below.",
  "Brag a little 😉 — what skills do you have?",
  "Go ahead — tell me your awesome skills! I’ll find the right job for you. 😎",
  "Tech wizard? Team player? Fast typer? Tell me everything! ✨",
  "Give me your skills — I’ll give you your future. 🔮",
  "You can write your skills however you want — a sentence, list, or even a paragraph.",
  "What kind of skills do you have? Type however you like!",
  "Tell me your skills — I’m all ears. 🎧",
  "Just describe your skills in your own words — I’ll do the rest!"
];

const compactGreetings = [
  "Input your skill set to initiate recommendation protocols.",
  "Job matching engine engaged. Awaiting input of your skillset.",
  "Processing unit is active. Kindly enter your skills."
];

// Add message with avatar and WhatsApp style alignment
function addMessage(text, sender, isTyping = false) {
  // Prevent adding empty non-typing messages
  if (!text && !isTyping) return;

  const wrapper = document.createElement("div");
  wrapper.classList.add("message-wrapper");
  if (sender === "user") wrapper.style.justifyContent = "flex-end";

  const lastMessage = chat.lastElementChild;
  let addAvatar = true;
  if (lastMessage && lastMessage.querySelector(".message")) {
    const lastSender = lastMessage.querySelector(".message").classList.contains("user") ? "user" : "bot";
    if (lastSender === sender) {
      addAvatar = false;
    }
  }

  const div = document.createElement("div");
  div.classList.add("message", sender);

  if (sender === "bot") {
    div.style.backgroundColor = "#13a4ec";
    div.style.color = "#fff";
  } else {
    div.style.backgroundColor = "#f0f3f4";
    div.style.color = "#111618";
  }

  if (isTyping) {
    div.classList.add("typing");
    div.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  } else if (sender === "bot") {
    div.textContent = "";
    typeWriter(div, text);
  } else {
    div.textContent = text;
  }

  if (addAvatar && !isTyping) { // Avoid avatar for typing dots
    const avatar = document.createElement("div");
    avatar.classList.add("avatar", sender === "user" ? "user-avatar" : "bot-avatar");
    avatar.innerHTML = sender === "user"
      ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.761 0 5-2.239 5-5s-2.239-5-5-5-5 2.239-5 5 2.239 5 5 5zm0 2c-3.86 0-7 3.14-7 7h2c0-2.761 2.239-5 5-5s5 2.239 5 5h2c0-3.86-3.14-7-7-7z"/></svg>`
      : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2c-4.963 0-9 4.037-9 9 0 3.867 2.462 7.176 5.879 8.444l-1.145 3.432 4.266-2.567c.325.029.656.046 1 .046 4.963 0 9-4.037 9-9s-4.037-9-9-9z"/></svg>`;

    if (sender === "user") {
      wrapper.appendChild(div);
      wrapper.appendChild(avatar);
    } else {
      wrapper.appendChild(avatar);
      wrapper.appendChild(div);
    }
  } else {
    wrapper.appendChild(div);
  }

  chat.appendChild(wrapper);

  // Auto-scroll to the newest message
  chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });

  return wrapper;
}

// Typing effect for bot messages
function typeWriter(element, text, i = 0) {
  if (i === 0) {
    element.innerHTML = `<span class="typed-text"></span><span class="cursor">|</span>`;
  }

  const typedText = element.querySelector(".typed-text");
  const cursor = element.querySelector(".cursor");

  if (i < text.length) {
    typedText.textContent += text.charAt(i);
    chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" }); // scroll during typing
    setTimeout(() => typeWriter(element, text, i + 1), 30);
  } else {
    cursor.remove();
    chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" }); // final scroll after typing done
  }
}

// Get random greeting based on mode
function greetBot() {
  const greeting = mode === "chatty" ? getRandom(chattyGreetings) : getRandom(compactGreetings);
  addMessage(greeting, "bot");
}

// Main function to send message to backend
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  const typingDiv = addMessage("", "bot", true);

  try {
    const response = await fetch("https://skillmatch-1-alv6.onrender.com/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        skills: msg,
        mode: mode,
        session_id: sessionIds[mode]
      })
    });

    if (!response.ok) throw new Error("Server error: " + response.status);

    const data = await response.json();

    if (data.session_id) sessionIds[mode] = data.session_id;

    document.querySelectorAll(".typing").forEach(div => div.remove());

    if (Array.isArray(data.responses)) {
      data.responses.forEach(msg => addMessage(msg, "bot"));
    } else {
      addMessage(data.response || "Hmm, no response.", "bot");
    }
  } catch (error) {
    console.error("Error talking to backend:", error);
    typingDiv.remove();
    addMessage("Oops! Couldn’t connect to backend.", "bot");
  }

  input.value = "";
}

function toggleMode() {
  if (mode === "chatty") {
    chatUI.classList.remove("chatty-mode");
    chatUI.classList.add("compact-mode");
    mode = "compact";
  } else {
    chatUI.classList.remove("compact-mode");
    chatUI.classList.add("chatty-mode");
    mode = "chatty";
  }

  chat.innerHTML = "";
  greetBot();
}

function startChat(selectedMode) {
  if (selectedMode !== "chatty" && selectedMode !== "compact") selectedMode = "chatty";
  mode = selectedMode;

  home.classList.add("hidden");
  chatUI.classList.remove("hidden");

  setTimeout(() => {
    chatUI.classList.add("active");
    chatUI.classList.remove("chatty-mode", "compact-mode");
    chatUI.classList.add(mode + "-mode");

    setTimeout(() => {
      greetBot();
    }, 100);
  }, 50);
}

function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});


