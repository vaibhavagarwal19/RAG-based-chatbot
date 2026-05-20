const chatContainer = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");

function appendMessage(text, sender, sources = []) {
    const div = document.createElement("div");
    div.classList.add("message");
    div.classList.add(sender === "user" ? "from-user" : "from-bot");
    div.style.opacity = 0;
    div.style.transition = "opacity 0.3s";

    const body = document.createElement("div");
    body.textContent = text;
    div.appendChild(body);

    if (sources && sources.length > 0) {
        const cites = document.createElement("div");
        cites.className = "mt-2 pt-2 border-t border-gray-300 text-xs text-gray-600";
        cites.innerHTML = "<strong>Sources</strong><br>" + sources.map((s) => {
            const page = s.page != null ? `, p. ${s.page}` : "";
            const label = `[${s.id}] ${s.source}${page}`;
            return `<span class="block mt-1" title="${s.excerpt.replace(/"/g, "&quot;")}">${label}</span>`;
        }).join("");
        div.appendChild(cites);
    }

    const ts = document.createElement("span");
    ts.classList.add("ts");
    ts.textContent = new Date().toLocaleTimeString();
    div.appendChild(ts);

    chatContainer.appendChild(div);
    requestAnimationFrame(() => { div.style.opacity = 1; });
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// conversation state for follow-up questions
let conversation = [];

const indexStatusEl = document.getElementById("index-status");
let indexReady = false;

async function pollIndexStatus() {
    try {
        const resp = await fetch("/status");
        const data = await resp.json();
        indexReady = data.ready;

        if (data.building) {
            indexStatusEl.classList.remove("hidden");
            indexStatusEl.textContent =
                "Indexing your PDF in the background (first run may take several minutes)…";
            input.disabled = true;
            setTimeout(pollIndexStatus, 3000);
            return;
        }

        if (data.error) {
            indexStatusEl.classList.remove("hidden");
            indexStatusEl.textContent = `Index error: ${data.error}`;
            input.disabled = false;
            return;
        }

        if (!data.ready) {
            indexStatusEl.classList.remove("hidden");
            indexStatusEl.textContent = "No document index yet — upload a PDF to get started.";
            input.disabled = false;
            return;
        }

        indexStatusEl.classList.add("hidden");
        indexStatusEl.textContent = "";
        input.disabled = false;
    } catch (e) {
        console.error(e);
        setTimeout(pollIndexStatus, 5000);
    }
}

pollIndexStatus();

// clear chat helper
const clearBtn = document.getElementById("clear-chat");
clearBtn.addEventListener("click", () => {
    chatContainer.innerHTML = "";
    conversation = [];
});

form.addEventListener("submit", async (evt) => {
    evt.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;

    appendMessage(msg, "user");
    input.value = "";

    if (!indexReady) {
        appendMessage(
            "The document index is still being prepared. Please wait for the status message above to clear.",
            "bot"
        );
        return;
    }

    const loadingMsg = document.createElement("div");
    loadingMsg.classList.add("message", "from-bot");
    loadingMsg.textContent = "Thinking…";
    chatContainer.appendChild(loadingMsg);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const resp = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: msg, conversation }),
        });
        const data = await resp.json();
        loadingMsg.remove();
        if (data.answer) {
            appendMessage(data.answer, "bot", data.sources || []);
            conversation = data.conversation || conversation;
        } else {
            appendMessage("(no response)", "bot");
        }
    } catch (e) {
        loadingMsg.remove();
        appendMessage("Error communicating with server", "bot");
        console.error(e);
    }
});

// handle uploads
const uploadForm = document.getElementById("upload-form");
const uploadFile = document.getElementById("upload-file");
const uploadStatus = document.getElementById("upload-status");

uploadForm.addEventListener("submit", async (evt) => {
    evt.preventDefault();
    if (!uploadFile.files.length) {
        uploadStatus.textContent = "Select a PDF first.";
        return;
    }

    const file = uploadFile.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        const resp = await fetch("/upload", {
            method: "POST",
            body: formData,
        });
        const data = await resp.json();
        if (data.status === "success") {
            uploadStatus.textContent = `Uploaded ${data.filename} (${data.chunks_added} chunks)`;
        } else {
            uploadStatus.textContent = data.error || "Upload failed";
        }
    } catch (e) {
        uploadStatus.textContent = "Error uploading file";
        console.error(e);
    }
});
