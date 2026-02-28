const chatContainer = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");

function appendMessage(text, sender) {
    const div = document.createElement("div");
    div.classList.add("message");
    div.classList.add(sender === "user" ? "from-user" : "from-bot");
    div.textContent = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// conversation state for follow-up questions
let conversation = [];

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

    try {
        const resp = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: msg, conversation }),
        });
        const data = await resp.json();
        if (data.answer) {
            appendMessage(data.answer, "bot");
            // update conversation history from server if provided
            conversation = data.conversation || conversation;
        } else {
            appendMessage("(no response)", "bot");
        }
    } catch (e) {
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
