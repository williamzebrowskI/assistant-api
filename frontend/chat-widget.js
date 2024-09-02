(function() {
    console.log("Chat widget script loaded");

    // Create the chat button
    const chatButton = document.createElement('button');
    chatButton.className = 'chat-button';
    chatButton.innerHTML = '💬';
    chatButton.onclick = toggleChat;
    document.body.appendChild(chatButton);
    console.log("Chat button appended to body");

    // Create the chat widget container
    const chatWidget = document.createElement('div');
    chatWidget.className = 'widget-container';
    chatWidget.id = 'chat-widget';
    chatWidget.innerHTML = `
        <div class="header">Chat with OpenAI</div>
        <div class="messages-container" id="messages"></div>
        <div class="input-container">
            <input type="text" id="message" class="input" autocomplete="off" placeholder="Type a message...">
            <button class="button" id="send">Send</button>
        </div>
    `;
    document.body.appendChild(chatWidget);
    console.log("Chat widget appended to body");

    // Add styles
    const style = document.createElement('style');
    style.innerHTML = `
        .chat-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #007bff;
            color: #fff;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: background-color 0.3s;
        }
        .chat-button:hover {
            background-color: #0056b3;
        }
        .widget-container {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 400px;
            height: 500px;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            background-color: #fff;
            display: none;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background-color: #007bff;
            color: #fff;
            padding: 15px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        .messages-container {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background-color: #f9f9f9;
            display: flex;
            flex-direction: column;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            word-wrap: break-word;
            display: inline-block;
        }
        .message.user {
            background-color: #e9ecef;
            color: #000;
            align-self: flex-start;
            margin-right: auto;
        }
        .message.assistant {
            background-color: #007bff;
            color: #fff;
            align-self: flex-end;
            margin-left: auto;
        }
        .input-container {
            display: flex;
            padding: 15px;
            border-top: 1px solid #ccc;
            background-color: #fff;
        }
        .input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-right: 10px;
            font-size: 16px;
        }
        .button {
            padding: 10px 15px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #0056b3;
        }
    `;
    document.head.appendChild(style);

    // Add scripts
    const socketIoScript = document.createElement('script');
    socketIoScript.src = 'https://cdn.socket.io/4.0.0/socket.io.min.js';
    document.head.appendChild(socketIoScript);

    const markedScript = document.createElement('script');
    markedScript.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(markedScript);

    // Initialize chat functionality
    socketIoScript.onload = markedScript.onload = function() {
        console.log("Socket.IO and Marked libraries loaded");

        let userId = localStorage.getItem("userId") || crypto.randomUUID();
        let conversationId = localStorage.getItem("conversationId") || crypto.randomUUID();
        localStorage.setItem("userId", userId);
        localStorage.setItem("conversationId", conversationId);

        var socket = io.connect('http://localhost:8002/chat', {
            query: { 'userId': userId, 'conversationId': conversationId }
        });

        function sendHeartbeat() {
            socket.emit('heartbeat', { message: 'ping' });
        }

        setInterval(sendHeartbeat, 60000);

        document.getElementById("message").addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                document.getElementById("send").click();
            }
        });

        socket.on('connect', function() {
            console.log('Connected to Socket.IO server');
        });

        socket.on('connect_error', function(error) {
            console.error('Socket.IO connection error:', error);
        });

        socket.on('assistant_message', function (data) {
            console.log('Received assistant message:', data);
            const messagesList = document.getElementById("messages");
            let lastMessage = messagesList.lastElementChild;
            if (!lastMessage || lastMessage.classList.contains("user")) {
                lastMessage = document.createElement("div");
                lastMessage.classList.add("message", "assistant");
                messagesList.appendChild(lastMessage);
                accumulatedMarkdown = '';
            }

            accumulatedMarkdown += data.text;

            lastMessage.innerHTML = marked.parse(accumulatedMarkdown);

            messagesList.scrollTop = messagesList.scrollHeight;
        });

        document.getElementById("send").addEventListener("click", function () {
            var messageText = document.getElementById("message").value.trim();
            if (!messageText) return;

            console.log('Sending user message:', messageText);
            socket.emit('user_message', {
                text: messageText,
                userId: userId,
                conversationId: conversationId,
            });

            const messagesList = document.getElementById("messages");
            const userMsgElement = document.createElement("div");
            userMsgElement.classList.add("message", "user");
            userMsgElement.innerText = messageText;
            messagesList.appendChild(userMsgElement);

            document.getElementById("message").value = '';
            messagesList.scrollTop = messagesList.scrollHeight;
        });

        console.log("Chat functionality initialized");
    };

    function toggleChat() {
        const chatWidget = document.getElementById('chat-widget');
        if (chatWidget.style.display === 'none' || chatWidget.style.display === '') {
            chatWidget.style.display = 'flex';
        } else {
            chatWidget.style.display = 'none';
        }
    }

    console.log("Chat widget script fully loaded");
})();