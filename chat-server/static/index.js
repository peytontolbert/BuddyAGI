
activetasks = {}

const appendMessage = (message) => {
    if (message.task_id) {
        appendTaskComponent(message);
    } else {
        if(message.user) {
        $("#chatBox").append("<p>" + message.user + ": " + message.message + "</p>");
    } else {
        console.log("No user in message")
    }}
};
const updateTasks = (chatId) => {
    $('#taskContainer').empty(); // Clear existing tasks
    const tasks = activetasks[chatId]; // Fetch tasks associated with the chatId
    header = `<h3>Tasks</h3>`
    $("#taskContainer").append(header);
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

const loadChatsFromStorage = () => {
    return JSON.parse(localStorage.getItem('chats')) || {};
};
const updateActiveTask = (activetask) => {
    $('#activeTasks').empty(); // Clear the container before adding new tasks
    // Assuming activetask contains fields like 'description'
    const taskHtml = `<div class='task-component'><p>${activetask.description}</p></div>`;
    $('#activeTasks').html(taskHtml); // Corrected ID selector
};
const updateCompletedTasks = (completedtasks) => {
    $('#completedTasks').empty(); // Clear existing completed tasks
    completedtasks.forEach(task => {
        // Update UI for each completed task
        // For example, moving the task to a 'completed' section
        const completedTaskHtml = `<div class='task-component completed'><p>${task.description}</p></div>`;
        $('#completedTasks').append(completedTaskHtml); // Assuming a div for completed tasks
    });
};
const updateNavbar = () => {
    const chats = loadChatsFromStorage();
    const navbar = $("#chatList").empty();
    Object.keys(chats).forEach(chatId => {
        const button = $('<button>').text(chatId).click(() => switchChat(chatId));
        navbar.append(button);
    });
    navbar.show();
};

$(document).ready(function() {
    let username = '';
    let currentChatId = '';
    let completedtasks = [];
    let lastMessageCount = 0; // This will keep track of the number of messages already displayed

    // Check if username is already set in local storage or session
    let storedUsername = localStorage.getItem('username'); // Example, replace with your actual storage key
    if (storedUsername) {
        // Username is set, so show the chat and tasks
        $("#startChatButton").show();
        $("#chatBox").show();
        $("#activeTasks").show();
        $("#completedTasks").show();
        updateNavbar();
        $('#toggleChatList').click(function() {
        $('#chatList').slideToggle(); // This will show or hide the chat list with a sliding motion
        });
        $("#navbar").show();
        $("#userInput").show().prop('disabled', false);
        $("#sendButton").show().prop('disabled', false);
        $("#usernameButton").hide().prop('disabled', true);
        $("#usernameInput").prop('disabled', true);
        // Populate the input field with the stored username
        $("#usernameInput").val(storedUsername);
    } else {
        // Username is not set, so hide the chat and tasks
        $("#startChatButton").hide();
        $("#chatBox").hide();
        $("#activeTasks").hide();
        $("#completedTasks").hide();
        $("#userInput").hide().prop('disabled', true);
        $("#sendButton").hide().prop('disabled', true);
        $("#taskContainer").hide();
    }

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

    const generateChatId = () => {
        return 'chat_' + Math.random().toString(36).substr(2, 9);
    };

    $("#usernameButton").click(function() {
        username = $("#usernameInput").val();
        if (username) {
            localStorage.setItem('username', username);
            $("#usernameInput").hide().prop('disabled', true);
            $("#usernameButton").hide().prop('disabled', true);
            $("#taskContainer").show();
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
    var username = localStorage.getItem('username');
    fetch('http://localhost:5000/getmessages', {
        method: 'POST', // Using POST to send data
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'user': username, 'chat_id': currentChatId })
    })
    .then(response => response.json())
    .then((data) => {
            console.log(data)
        // data will contain all of the messages from the chatbox such as { messages: [{P: Hey}, {AI: How are you?}]}
        // If there are new messages, append them to the chat box
        if (data.messages) {
            updateChat(data.messages);
            activetaskmessage = data.activetask;
            completedtasks = data.completedtasks;
        if (activetaskmessage) {
            updateActiveTask(activetaskmessage)
        }
        if (completedtasks) {
            updateCompletedTasks(completedtasks)
        } 
    }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};
const updateChat = (messages) => {
    const newMessages = messages.slice(lastMessageCount);
    if (newMessages) {
    $("#userInput").prop('disabled', false);
    $("#sendButton").prop('disabled', false);
    }
    newMessages.forEach(message => {
        appendMessage(message);
        saveChatToStorage(currentChatId, chats[currentChatId]);
    });
    lastMessageCount = messages.length; // Update the last message count
};

// Start polling for new messages every few seconds
setInterval(pollForNewMessages, 5000); // Poll every 5 seconds

    $("#sendButton").click(function() {
        var userInput = $("#userInput").val();
        var username = localStorage.getItem('username');
        const message = username + ": " + $("#userInput").val();
        if(userInput && currentChatId != '') {
            const chats = loadChatsFromStorage();
            chats[currentChatId] = chats[currentChatId] || [];
            chats[currentChatId].push(message);
            saveChatToStorage(currentChatId, chats[currentChatId]);
            // Add user's message to chat
            appendMessage({ 'user': username, 'message': userInput });
            lastMessageCount += 1;  // Increment the message count

            // Disable input and send button
            $("#userInput").prop('disabled', true);
            $("#sendButton").prop('disabled', true);

            // Send the user's message to the server and get the response
            fetch('http://localhost:5000/pinghelper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'user': username, 'message': userInput, 'chat_id': currentChatId }),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                $("#userInput").val("");
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
});
