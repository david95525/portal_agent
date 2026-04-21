let isLgOpen = false;
let isLcOpen = false;
let userToken = "";

// 建議問題配置
const suggestionsConfig = {
    main: [
        { label: "📊 查詢血壓紀錄", value: "search" },
        { label: "📈 統計數據 (平均/最大/最小)", value: "stats" },
        { label: "💬 隨便聊聊", value: "general" }
    ],
    search: [
        { label: "上週", text: "幫我查詢上週的血壓紀錄" },
        { label: "一個月內", text: "幫我查詢一個月內的血壓紀錄" },
        { label: "三個月內", text: "幫我查詢三個月內的血壓紀錄" },
        { label: "自訂", text: "自訂查詢：" },
        { label: "⬅ 返回", value: "main" }
    ],
    stats: [
        { label: "平均值", value: "stats_range", extra: "平均值" },
        { label: "最大值", value: "stats_range", extra: "最大值" },
        { label: "最小值", value: "stats_range", extra: "最小值" },
        { label: "⬅ 返回", value: "main" }
    ],
    stats_range: (metric) => [
        { label: `上週${metric}`, text: `我想知道上週血壓的${metric}` },
        { label: `一個月內${metric}`, text: `我想知道一個月內血壓的${metric}` },
        { label: `三個月內${metric}`, text: `我想知道三個月內血壓的${metric}` },
        { label: "⬅ 返回", value: "stats" }
    ]
};

// 渲染建議按鈕
function renderSuggestions(type, category = "main", extra = null) {
    const container = document.getElementById(`${type}-suggestions`);
    container.innerHTML = "";
    
    let options = [];
    if (typeof suggestionsConfig[category] === 'function') {
        options = suggestionsConfig[category](extra);
    } else {
        options = suggestionsConfig[category];
    }

    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "suggestion-btn";
        btn.innerText = opt.label;
        btn.onclick = () => {
            if (opt.text) {
                // 如果有最終文字，發送訊息
                if (opt.label === "自訂") {
                    const input = document.getElementById(`${type}-input`);
                    input.value = opt.text;
                    input.focus();
                } else {
                    executeSendMessage(type, opt.text);
                    renderSuggestions(type, "main"); // 回到主選單
                }
            } else if (opt.value) {
                // 如果是下一層
                renderSuggestions(type, opt.value, opt.extra);
            }
        };
        container.appendChild(btn);
    });
}

function toggleChats() {
    isLgOpen = !isLgOpen;
    isLcOpen = !isLcOpen;
    const lgWin = document.getElementById('chat-window-langgraph');
    const lcWin = document.getElementById('chat-window-langchain');
    lgWin.style.display = isLgOpen ? 'flex' : 'none';
    lcWin.style.display = isLcOpen ? 'flex' : 'none';
    
    if (isLgOpen) renderSuggestions('langgraph');
    if (isLcOpen) renderSuggestions('langchain');
}

function closeChat(type) {
    if (type === 'langgraph') {
        isLgOpen = false;
        document.getElementById('chat-window-langgraph').style.display = 'none';
    } else {
        isLcOpen = false;
        document.getElementById('chat-window-langchain').style.display = 'none';
    }
}

function saveToken() {
    const input = document.getElementById('token-input');
    userToken = input.value.trim();
    if (userToken) {
        document.getElementById('token-input-container').classList.add('hidden');
        document.getElementById('token-display').classList.remove('hidden');
    }
}

function editToken() {
    document.getElementById('token-input-container').classList.remove('hidden');
    document.getElementById('token-display').classList.add('hidden');
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

async function sendMessage(type) {
    const input = document.getElementById(`${type}-input`);
    const text = input.value.trim();
    if (!text) return;
    executeSendMessage(type, text);
    input.value = "";
}

async function executeSendMessage(type, text) {
    if (!userToken) {
        alert("Please enter User Token first!");
        return;
    }

    appendMessage(type, 'user', text);

    const endpoint = type === 'langgraph' ? '/api/v1/bp/chat' : '/api/v1/langchain/chat';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: "demo-user",
                message: text,
                user_token: userToken
            })
        });

        const data = await response.json();
        appendMessage(type, 'agent', data.text);
        
        if (type === 'langgraph' && data.intent) {
            updateGraphHighlight(data.intent);
        }
    } catch (error) {
        console.error(error);
        appendMessage(type, 'agent', "Error: Could not connect to the server.");
    }
}

function appendMessage(type, sender, text) {
    const container = document.getElementById(`${type}-messages`);
    const div = document.createElement('div');
    div.className = `message ${sender}-message`;
    div.innerText = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.mermaid) {
        mermaid.run();
    }
});

window.toggleChats = toggleChats;
window.closeChat = closeChat;
window.saveToken = saveToken;
window.editToken = editToken;
window.sendMessage = sendMessage;
