const API = "http://127.0.0.1:8000";  // your server, on this computer only
let sessionId = null;                  // the "ticket" from /start

const $ = (id) => document.getElementById(id);  // shortcut for finding page elements

// Add a line to the chat. textContent (not innerHTML) shows text as plain text,
// so a page's hidden code can never run inside the extension.
// Add a chat bubble. who is "user" or "bot", which matches the CSS class names.
// textContent keeps page text from ever running as code.
function addBubble(who, text) {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;
  div.textContent = text;
  $("log").appendChild(div);
  div.scrollIntoView();  // keep the newest message in view
  return div;            // returned so we can remove it later
}

// A bot bubble holding three dots. The innerHTML here is a fixed string we
// wrote ourselves, never page content, so it's safe.
function showTyping() {
  const div = addBubble("bot", "");
  div.classList.add("typing");
  div.innerHTML = "<span></span><span></span><span></span>";
  return div;
}

// Send data to the server and return its reply. Throws an error with a readable message.
async function post(path, body) {
  let response;
  try {
    response = await fetch(API + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Can't reach the server. Is uvicorn running?");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail);  // "detail" holds our friendly error text
  return data;
}

$("load").onclick = async () => {
  // Ask Chrome which tab is open in front of you
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url || !tab.url.startsWith("http")) {
    $("status").textContent = "Can't read this tab (Chrome's own pages aren't supported).";
    return;
  }
  sessionId = null;
  $("log").textContent = "";       // clear the old chat
  $("status").textContent = "Loading page...";
  $("question").disabled = $("send").disabled = true;
  try {
    const data = await post("/start", { url: tab.url });
    sessionId = data.session_id;
    $("status").textContent = `Loaded (${data.words} words)` +
      (data.truncated
        ? `. Note: Due to model size constraints, I can only answer questions about the first ${data.percent_read}% of the page.`
        : ".");
    $("question").disabled = $("send").disabled = false;
  } catch (error) {
    $("status").textContent = error.message;  // paywall, captcha, etc.
  }
};

$("send").onclick = async () => {
  const question = $("question").value.trim();
  if (!question) return;
  addBubble("user", question);
  $("question").value = "";
  $("send").disabled = true;       // block double-clicks while the model thinks
  $("status").textContent = "";
  const typing = showTyping();     // dots appear while we wait
  try {
    const data = await post("/ask", { session_id: sessionId, question });
    typing.remove();               // swap the dots for the real answer
    addBubble("bot", data.answer);
  } catch (error) {
    typing.remove();
    $("status").textContent = error.message;
  }
  $("send").disabled = false;
};