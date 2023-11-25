$(document).ready(function() {
    let username = '';
    let currentChatId = '';
    let lastMessageCount = 0; // This will keep track of the number of messages already displayed

    const loadChatsFromStorage = () => {
        return JSON.parse(localStorage.getItem('chats')) || {};
    };

    const saveChatToStorage = (chatId, messages) => {
        const chats = loadChatsFromStorage();
        chats[chatId] = messages;
        localStorage.setItem('chats', JSON.stringify(chats));
    };

    const switchChat = (chatId) => {
        currentChatId = chatId;
        $("#chatBox").empty();
        const chats = loadChatsFromStorage();
        if (chats[chatId]) {
            chats[chatId].forEach(msg => appendMessage(msg));
        }
        // Update UI for the current chat
        $("#chatBox").show();
        $("#userInput").show().prop('disabled', false);
        $("#sendButton").show().prop('disabled', false);
        updateTasks(chatId);
    };

    const updateNavbar = () => {
        const chats = loadChatsFromStorage();
        const navbar = $("#navbar").empty();
        Object.keys(chats).forEach(chatId => {
            const button = $('<button>').text(chatId).click(() => switchChat(chatId));
            navbar.append(button);
        });
        navbar.show();
    };

    const generateChatId = () => {
        return 'chat_' + Math.random().toString(36).substr(2, 9);
    };

    $("#usernameButton").click(function() {
        username = $("#usernameInput").val();
        if (username) {
            $("#usernameInput").prop('disabled', true);
            $("#usernameButton").prop('disabled', true);
            $("#startChatButton").show();
            updateNavbar();
        }
    });
    
    $("#startChatButton").click(function() {
        const newChatId = generateChatId();
        saveChatToStorage(newChatId, []);
        switchChat(newChatId);
        updateNavbar();
    });
// Function to poll for new messages from the server
const pollForNewMessages = () => {
    fetch('http://localhost:5000/getmessages', {
        method: 'POST', // Using POST to send data
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user: username, chat_id: currentChatId })
    })
    .then(response => response.json())
    .then(data => {
        // data will contain all of the messages from the chatbox such as { messages: [{P: Hey}, {AI: How are you?}]}
        // If there are new messages, append them to the chat box
        if (data && data.messages) {
            
        if (data.task && data.task.complete) {
            const task = activetasks[currentChatId][data.task.task_id]
            if (task) {
                task.complete = true;
                updateTasks(currentChatId);
                completedtasks[currentChatId] = task;
                delete activetasks[currentChatId][data.task.task_id];
            }
            activetasks[currentChatId] = data.task_id;
            updateTasks(currentChatId);
        } else {
            console.log(data);
            const newMessages = data.messages.slice(lastMessageCount);
            newMessages.forEach(message => {
                // Assuming message structure is { user: 'P', message: 'Hey'}
                appendMessage(message);
            });
            lastMessageCount = data.messages.length; // Update the last message count
        }
    }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

// Start polling for new messages every few seconds
setInterval(pollForNewMessages, 5000); // Poll every 5 seconds

    $("#sendButton").click(function() {
        var userInput = $("#userInput").val();
        const message = username + ": " + $("#userInput").val();
        const chats = loadChatsFromStorage();
        chats[currentChatId] = chats[currentChatId] || [];
        chats[currentChatId].push(message);
        saveChatToStorage(currentChatId, chats[currentChatId]);
        if(userInput) {
            // Add user's message to chat
            appendMessage(message);
            lastMessageCount += 1;  // Increment the message count

            // Send the user's message to the server and get the response
            fetch('http://localhost:5000/pinghelper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user: username, message: userInput, chat_id: currentChatId }),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                // Clear the input field
                $("#userInput").val("");
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
});


const appendMessage = (message) => {
    if (message.task_id) {
        appendTaskComponent(message);
    } else {
        $("#chatBox").append("<p>" + message.user + ": " + message.message + "</p>");
    }
};
const updateTasks = (chatId) => {
    $('#taskContainer').empty(); // Clear existing tasks
    const tasks = activetasks[chatId]; // Fetch tasks associated with the chatId
    if (tasks) {
        tasks.forEach(task => appendTaskComponent(task));
    }
};

const appendTaskComponent = (taskMessage) => {
    let taskComponent = `
        <div class="task-component" id="task-${taskMessage.task_id}">
            <p><strong>Task:</strong> ${taskMessage.message}</p>
    `;
        if (taskMessage.require_reply) {
            taskComponent += `
            <input type="text" id="reply-${taskMessage.task_id}" placeholder="Type your reply..." />
            <button onclick="sendTaskReply('${taskMessage.task_id}')">Send Reply</button>
        `;
    }
    taskComponent+=  `</div>`;
    $("#taskContainer").append(taskComponent);
};


// Function to send task reply to the server
const sendTaskReply = (taskId) => {
    const replyMessage = $(`#reply-input-${taskId}`).val();
    if(replyMessage) {
        fetch('http://localhost:5000/replytotask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                user: username, 
                task_id: taskId, 
                reply: replyMessage,
                chat_id: currentChatId,
                complete: true 
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Clear the input field after sending the reply
            $(`#reply-input-${taskId}`).val('');
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
};