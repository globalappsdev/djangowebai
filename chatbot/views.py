# chatbot/views.py
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .utils import send_telegram_message, sendtoAi, USER_HISTORIES, USER_AGENT_CHATS, ACTIVE_CHATS
from django.conf import settings

def chatbot_js(request):
    js_code = """
    (function() {
        let existingContainer = document.getElementById('chatbot-container');
        if (existingContainer) {
            existingContainer.parentNode.removeChild(existingContainer);
        }

        var chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'chatbot-container';
        chatbotContainer.style.position = 'fixed';
        chatbotContainer.style.bottom = '20px';
        chatbotContainer.style.right = '20px';
        chatbotContainer.style.width = '350px';
        chatbotContainer.style.height = '500px';
        chatbotContainer.style.background = '#ffffff';
        chatbotContainer.style.borderRadius = '10px';
        chatbotContainer.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        chatbotContainer.style.display = 'none';
        chatbotContainer.style.flexDirection = 'column';
        chatbotContainer.style.justifyContent = 'space-between';
        chatbotContainer.style.fontFamily = 'Arial, sans-serif';

        chatbotContainer.innerHTML = `
            <div id='chatbot-header' style='background: #007bff; color: white; padding: 15px; text-align: center; font-weight: bold; cursor: pointer; border-top-left-radius: 10px; border-top-right-radius: 10px; display: flex; justify-content: space-between;'>
                <span>Chat with AI</span>
                <button id='close-chatbot' style='background: transparent; border: none; color: white; font-size: 16px; cursor: pointer;'>✕</button>
            </div>
            <div id='chatbot-messages' style='flex: 1; padding: 10px; overflow-y: auto; max-height: 400px;'></div>
            <div id='chatbot-input-area' style='display: flex; padding: 10px; border-top: 1px solid #ccc;'>
                <input id='chatbot-input' type='text' placeholder='Type a message...' style='flex: 1; border: none; padding: 10px; border-radius: 5px;'>
                <button id='send-message' style='background: #007bff; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px; margin-left: 5px;'>Send</button>
            </div>
        `;

        document.body.appendChild(chatbotContainer);

        var toggleButton = document.createElement('button');
        toggleButton.innerText = 'Chat 💬';
        toggleButton.id = 'chatbot-toggle';
        toggleButton.style.position = 'fixed';
        toggleButton.style.bottom = '20px';
        toggleButton.style.right = '20px';
        toggleButton.style.background = '#007bff';
        toggleButton.style.color = 'white';
        toggleButton.style.border = 'none';
        toggleButton.style.padding = '10px 15px';
        toggleButton.style.borderRadius = '5px';
        toggleButton.style.cursor = 'pointer';
        toggleButton.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.2)';
        document.body.appendChild(toggleButton);

        // Generate unique user ID
        const userId = 'user_' + Math.random().toString(36).substr(2, 9);

        // Dynamically determine base URL from script source
        const scriptTag = document.currentScript;
        const baseUrl = scriptTag.src.replace('/chatbot.js', '');
        
        // WebSocket connection
        const socket = new WebSocket(baseUrl.replace('http', 'ws') + '/ws/chat/' + userId + '/');
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            let messagesDiv = document.getElementById('chatbot-messages');
            let botMessage = document.createElement('div');
            botMessage.innerHTML = data.response;
            botMessage.style.background = '#e9ecef';
            botMessage.style.color = '#333';
            botMessage.style.padding = '10px';
            botMessage.style.margin = '5px';
            botMessage.style.borderRadius = '10px';
            botMessage.style.alignSelf = 'flex-start';
            messagesDiv.appendChild(botMessage);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };

        socket.onerror = function(error) {
            console.error('WebSocket Error:', error);
        };

        document.getElementById('chatbot-toggle').addEventListener('click', function() {
            if (chatbotContainer.style.display === 'none') {
                chatbotContainer.style.display = 'flex';
                toggleButton.style.display = 'none';
            } else {
                chatbotContainer.style.display = 'none';
                toggleButton.style.display = 'block';
            }
        });

        document.getElementById('close-chatbot').addEventListener('click', function() {
            chatbotContainer.style.display = 'none';
            toggleButton.style.display = 'block';
        });

        function sendMessage() {
            let inputField = document.getElementById('chatbot-input');
            let message = inputField.value.trim();
            if (message !== '') {
                let messagesDiv = document.getElementById('chatbot-messages');

                let userMessage = document.createElement('div');
                userMessage.innerHTML = message;
                userMessage.style.background = '#007bff';
                userMessage.style.color = 'white';
                userMessage.style.padding = '10px';
                userMessage.style.margin = '5px';
                userMessage.style.borderRadius = '10px';
                userMessage.style.alignSelf = 'flex-end';
                messagesDiv.appendChild(userMessage);

                inputField.value = '';

                // Add typing indicator
                let typingMessage = document.createElement('div');
                typingMessage.innerHTML = 'Typing...';
                typingMessage.style.background = '#e9ecef';
                typingMessage.style.color = '#333';
                typingMessage.style.padding = '10px';
                typingMessage.style.margin = '5px';
                typingMessage.style.borderRadius = '10px';
                typingMessage.style.alignSelf = 'flex-start';
                messagesDiv.appendChild(typingMessage);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                fetch(baseUrl + '/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message, userId: userId })
                })
                .then(response => response.json())
                .then(data => {
                    messagesDiv.removeChild(typingMessage);
                    let botMessage = document.createElement('div');
                    botMessage.innerHTML = data.response;
                    botMessage.style.background = '#e9ecef';
                    botMessage.style.color = '#333';
                    botMessage.style.padding = '10px';
                    botMessage.style.margin = '5px';
                    botMessage.style.borderRadius = '10px';
                    botMessage.style.alignSelf = 'flex-start';
                    messagesDiv.appendChild(botMessage);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                })
                .catch(error => {
                    messagesDiv.removeChild(typingMessage);
                    console.error('Error:', error);
                    let errorMessage = document.createElement('div');
                    errorMessage.innerHTML = 'Oops! Something went wrong.';
                    errorMessage.style.background = '#ffcccc';
                    errorMessage.style.color = '#333';
                    errorMessage.style.padding = '10px';
                    errorMessage.style.margin = '5px';
                    errorMessage.style.borderRadius = '10px';
                    errorMessage.style.alignSelf = 'flex-start';
                    messagesDiv.appendChild(errorMessage);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                });
            }
        }

        document.getElementById('send-message').addEventListener('click', sendMessage);
        document.getElementById('chatbot-input').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') sendMessage();
        });
    })();
    """
    response = HttpResponse(js_code, content_type='application/javascript')
    response['Access-Control-Allow-Origin'] = '*'  # For development; adjust for production
    return response
    
@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        user_id = data.get('userId', str(uuid.uuid4()))

        if user_id not in USER_HISTORIES:
            USER_HISTORIES[user_id] = []
        if user_id not in USER_AGENT_CHATS:
            USER_AGENT_CHATS[user_id] = {"is_agent_chat": False, "telegram_chat_id": None}
        
        user_history = USER_HISTORIES[user_id]
        user_agent_chat = USER_AGENT_CHATS[user_id]

        if "chat with agent" in user_message or "talk to agent" in user_message:
            user_agent_chat["is_agent_chat"] = True
            user_agent_chat["telegram_chat_id"] = settings.TELEGRAM_AGENT_CHAT_ID
            message_to_agent = f"[{user_id}] User requested agent chat: {user_message}"
            send_telegram_message(settings.TELEGRAM_AGENT_CHAT_ID, message_to_agent)
            bot_response = "I’ve notified an agent. They’ll join the chat soon."
            user_history.append({"user": user_message, "bot": bot_response})
            response = JsonResponse({"response": bot_response})
        elif user_agent_chat["is_agent_chat"]:
            message_to_agent = f"[{user_id}] {user_message}"
            send_telegram_message(settings.TELEGRAM_AGENT_CHAT_ID, message_to_agent)
            bot_response = "Message sent to agent. Please wait for their reply."
            user_history.append({"user": user_message, "bot": bot_response})
            response = JsonResponse({"response": bot_response})
        else:
            response_text = sendtoAi(user_message, user_history)
            try:
                response_json = json.loads(response_text)
                bot_response = response_json["response"]
            except json.JSONDecodeError:
                bot_response = "Sorry, I couldn’t process that. How can I assist you?"
            
            user_history.append({"user": user_message, "bot": bot_response})
            if len(user_history) > 10:
                user_history.pop(0)
            response = JsonResponse({"response": bot_response})
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = '*'  # For development; restrict in production
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Handle non-POST requests (e.g., OPTIONS for CORS preflight)
    response = JsonResponse({"error": "Method not allowed"}, status=405)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        update = json.loads(request.body)
        if "message" in update:
            message = update["message"]
            chat_id = str(message["chat"]["id"])
            text = message["text"]

            if chat_id == settings.TELEGRAM_AGENT_CHAT_ID:
                try:
                    user_id_start = text.index("[") + 1
                    user_id_end = text.index("]")
                    user_id = text[user_id_start:user_id_end]
                    agent_reply = text[user_id_end + 1:].strip()

                    if user_id in USER_HISTORIES:
                        USER_HISTORIES[user_id].append({"user": "(agent)", "bot": agent_reply})
                        # Push to WebSocket
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f"chat_{user_id}",
                            {
                                "type": "chat_message",
                                "response": f"Agent: {agent_reply}"
                            }
                        )
                except ValueError:
                    send_telegram_message(settings.TELEGRAM_AGENT_CHAT_ID, 
                                        "Please include [user_id] in your reply, e.g., [user_abc123] Hi")
    
    return JsonResponse({"status": "ok"})
