
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova AI Support</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background-color: #131822;
            color: #e2e8f0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .chat-wrapper {
            width: 100%;
            max-width: 750px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }

        /* Header Section */
        .header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 24px;
            font-size: 1.1rem;
        }

        .header-title {
            font-weight: 600;
            color: #ffffff;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            margin-left: 4px;
        }

        .status-text {
            font-size: 0.85rem;
            color: #22c55e;
            font-weight: 500;
        }

        /* Chat Messages Container */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            padding-right: 8px;
            scroll-behavior: smooth;
        }

        .chat-messages::-webkit-scrollbar {
            width: 4px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        /* Message Items */
        .message {
            max-width: 82%;
            font-size: 0.95rem;
            line-height: 1.55;
            animation: fadeIn 0.25s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Bot Message: Plain text floating on dark canvas */
        .message.bot {
            align-self: flex-start;
            color: #e2e8f0;
            font-weight: 400;
        }

        /* User Message: Yellow Pill Bubble */
        .message.user {
            align-self: flex-end;
            background-color: #facc15;
            color: #111827;
            font-weight: 500;
            padding: 10px 18px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }

        /* Typing Indicator */
        .typing {
            display: none;
            align-self: flex-start;
            color: #94a3b8;
            font-size: 0.85rem;
            font-style: italic;
            padding-top: 4px;
        }

        /* Footer Input Section */
        .input-section {
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 8px;
            transition: border-color 0.2s ease;
        }

        .input-wrapper:focus-within {
            border-bottom-color: #facc15;
        }

        input[type="text"] {
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: #f8fafc;
            font-size: 0.95rem;
            padding-right: 40px;
        }

        input[type="text"]::placeholder {
            color: #64748b;
        }

        .send-btn {
            position: absolute;
            right: 0;
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
            transition: transform 0.15s ease;
        }

        .send-btn:hover {
            transform: scale(1.1);
        }

        .send-btn svg {
            width: 20px;
            height: 20px;
            fill: #facc15;
        }
    </style>
</head>
<body>
    <div class="chat-wrapper">
        <!-- Minimal Header -->
        <div class="header">
            <span class="header-title">Nova</span>
            <span class="status-dot"></span>
            <span class="status-text">Online</span>
        </div>

        <!-- Messages Area -->
        <div class="chat-messages" id="chatMessages">
        </div>

        <div class="typing" id="typingIndicator">Nova is thinking & querying database...</div>

        <!-- Input Area -->
        <div class="input-section">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Type your support request here..." onkeypress="handleKeyPress(event)" autofocus>
                <button class="send-btn" onclick="sendMessage()" title="Send Message">
                    <svg viewBox="0 0 24 24">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let chatHistory = [];

        function appendMessage(role, text) {
            const messagesDiv = document.getElementById('chatMessages');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${role}`;
            msgDiv.innerText = text;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const inputEl = document.getElementById('userInput');
            const text = inputEl.value.trim();
            if (!text) return;

            appendMessage('user', text);
            inputEl.value = '';

            const typing = document.getElementById('typingIndicator');
            typing.style.display = 'block';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: text,
                        chat_history: chatHistory
                    })
                });

                const data = await response.json();
                typing.style.display = 'none';

                if (response.ok) {
                    appendMessage('bot', data.response);
                    chatHistory.push({ role: 'user', content: text });
                    chatHistory.push({ role: 'assistant', content: data.response });
                } else {
                    appendMessage('bot', 'Error: ' + (data.detail || 'Could not process request.'));
                }
            } catch (err) {
                typing.style.display = 'none';
                appendMessage('bot', 'Network error. Ensure FastAPI server is running.');
            }
        }
    </script>
</body>
</html>

