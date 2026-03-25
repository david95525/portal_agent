let isChatOpen = false;
let userToken = "";

function toggleChat() {
    const win = document.getElementById('chat-window');
    isChatOpen = !isChatOpen;
    win.style.display = isChatOpen ? 'flex' : 'none';
}

function saveToken() {
    const input = document.getElementById('token-input');
    const container = document.getElementById('token-input-container');
    const display = document.getElementById('token-display');
    
    userToken = input.value.trim();
    if (userToken) {
        container.classList.add('hidden');
        display.classList.remove('hidden');
    }
}

function editToken() {
    const container = document.getElementById('token-input-container');
    const display = document.getElementById('token-display');
    
    container.classList.remove('hidden');
    display.classList.add('hidden');
}

async function renderMermaid() {
    if (window.mermaid) {
        const container = document.getElementById('mermaid-graph');
        container.removeAttribute('data-processed');
        await mermaid.run({ nodes: [container] });
    }
}

async function updateGraphHighlight(intent) {
    const container = document.getElementById('mermaid-graph');
    let baseGraph = `graph TD
    START((START)) --> router{Router}
    router -- search/stats --> search[Search Data]
    search -- stats --> stats[Analyze Stats]
    search -- end --> END((END))
    stats --> END
    router -- general --> general[General Node]
    general --> END

    classDef active stroke:#f00,stroke-width:4px;`;

    if (intent === 'search') baseGraph += "\nclass search active";
    if (intent === 'stats') baseGraph += "\nclass search,stats active";
    if (intent === 'general') baseGraph += "\nclass general active";

    container.innerHTML = baseGraph;
    container.removeAttribute('data-processed');
    await mermaid.run({ nodes: [container] });
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    if (!userToken) {
        alert("Please enter User Token in the Debug Console first!");
        return;
    }

    appendMessage('user', text);
    input.value = "";

    try {
        const response = await fetch('/api/v1/bp/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: "demo-user",
                message: text,
                user_token: userToken
            })
        });

        const data = await response.json();
        appendMessage('agent', data.text);
        if (data.intent) {
            updateGraphHighlight(data.intent);
        }
    } catch (error) {
        console.error(error);
        appendMessage('agent', "Error: Could not connect to the server.");
    }
}

function appendMessage(sender, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${sender}-message`;
    div.innerText = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Initial render
document.addEventListener('DOMContentLoaded', () => {
    renderMermaid();
});

// Expose functions to window for onclick handlers in HTML
window.toggleChat = toggleChat;
window.saveToken = saveToken;
window.editToken = editToken;
window.sendMessage = sendMessage;
