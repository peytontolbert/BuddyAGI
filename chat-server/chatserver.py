from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import json
import threading
import time
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'])
database_agentmessages = []
helpermessages = []
manageragentmessages = []
chats = {}
activetasks = {}
task_chats = []
completedtasks = {}
coding_agentmessages = []
# Function to save messages to a JSON file
def save_messages():
    # Create a lock to synchronize access to the messages list
    with app.app_context():
        data = {
            'database_agentmessages': database_agentmessages,
            'chats': chats,
            'helpermessages': helpermessages,
            'manageragentmessages': manageragentmessages,
            'activetasks': activetasks,
            'completedtasks': completedtasks,
            'coding_agentmessages': coding_agentmessages
        }
        # Save the messages list to a JSON file
        with open('messages.json', 'w') as f:
            json.dump(data, f)

    # Schedule the next save in 5 minutes
    threading.Timer(300, save_messages).start()

# Start saving messages in the background
save_messages()
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/pinghelper", methods=["POST"])
def pinghelperagent():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    chat_id = data.get('chat_id')
    print(message)
    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400
    # Find or create the chat in the chats list
    chat = chats.get(chat_id)
    if chat is None:
        # Create a new chat if not found
        chat = {'chat_id': chat_id, 'user': user, 'messages': [message], 'read': True}
        chats["chat_id"].update(chat)
    # Add the message to the messages list
    chat['messages'].append({'user': user, 'message': message})
    chat['read'] = False
    
    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/pingdbagent", methods=["POST"])
def pingdbagent():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    print(message)

    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    # Add the message to the messages list
    database_agentmessages.append({'user': user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/helpermessages", methods=["GET"])
def helpermessagess():
    unread_chats = []
    for chat in chats:
        print(chat)
        if not chat['read']:
            print(f'unread chat: {chat}')
            unread_chats.append(chat)
            chat['read'] = True
    if not unread_chats:
        return jsonify({'messages': 'No unread messages'}), 404
    return jsonify({'messages': unread_chats}), 200


@app.route("/dbagentmessages", methods=["GET"])
def dbagentmessagess():
    # Check if there are no messages
    if len(database_agentmessages) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    all_messages = database_agentmessages.copy()  # Copy the messages
    # Clear the messages list
    database_agentmessages.clear()

    return jsonify({'message': all_messages[-3:]}), 200


@app.route("/codingagentmessages", methods=["GET"])
def codingagentmessagess():
    # Check if there are no messages
    if len(coding_agentmessages) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    all_messages = coding_agentmessages.copy()  # Copy the messages
    # Clear the messages list
    coding_agentmessages.clear()

    return jsonify({'message': all_messages[-3:]}), 200

@app.route("/getmessages", methods=["POST"])
def getnewmessagess():
    data = request.get_json()
    user = data.get('user')
    chat_id = data.get('chat_id')
    # Find the chat in the chats list
    chat = chats.get(chat_id)
    if chat and chat['user'] == user:
        task_info = activetasks.get(chat_id)
        if task_info is not None:
            
            # Return the messages for this chat
            return jsonify({'messages': chat['messages'], 'task': task_info}), 200
        else:
            completed_task_info = completedtasks.get(chat_id)
            if completed_task_info is not None:
                return jsonify({'messages': chat['messages'], 'task': completed_task_info}), 200
            else:
                return jsonify({'messages': chat['messages']}), 200
    else:
        # If chat not found
        return jsonify({'status': 'failure', 'error': 'Chat not found'}), 404

@app.route("/managernewtask", methods=["POST"])
def assignmanagertask():
    data = request.get_json()
    chat_id = data.get('chat_id')
    message = data.get('message')
    user = data.get('sender')
    task_id = f"{user}_{int(time.time())}_{uuid.uuid4()}"
    messages = [{"role": "user", "content": f"Buddy: {message}"}]
    task_info = {'task_id': task_id, 'user': user, 'messages': messages}
    activetasks[task_id] = task_info
    chat = chats.get(chat_id)
    chat['messages'].append({'user': user, 'message': message, 'task_id': task_id})
    chats[chat_id] = chat
    return jsonify({'task_id': task_id}), 200

@app.route("/assigntask", methods=["POST"])
def assigntaskk():
    data = request.get_json()
    task_id = data.get('task_id')
    chat_id = data.get('chat_id')
    user = data.get('user')
    task = data.get('task')
    receiver = data.get('receiver')
    chat = chats.get(chat_id)
    active_task = activetasks.get(task_id)
    if active_task is not None and chat is not None:
        # Determine the receiver and append task message to the respective list
        if receiver.lower() in ['codingagent', 'dbagent']:
            # For coding or database agent, append to their respective message lists
            message_list = coding_agentmessages if receiver.lower() == 'codingagent' else database_agentmessages
            message_list.append({'task_id': task_id, 'chat_id': chat_id, 'user': user, 'message': task, 'complete_status': 'False'})
        elif receiver == user:
            # For user, add the task message to the chat
            chat['messages'].append({'user': user, 'message': task, 'task_id': task_id, 'require_reply': True})
            chats[chat_id] = chat  # Update the chat with the new message
        else:
            return jsonify({'status': 'failure', 'error': 'Invalid receiver'}), 400
    else:
        return jsonify({'status': 'failure', 'error': 'Task or chat not found'}), 404
    return jsonify({'status': 'success', 'message': 'Task assigned'}), 200


@app.route("/aitask", methods=["POST"])
def aitaskk():
    data = request.get_json()
    task_id = data.get('task_id')
    message = data.get('message')
    complete_status = data.get('complete_status')
    recipient = data.get('recipient')
    if complete_status == 'True':
        helpermessages.append({'task_id': task_id, 'message': message, complete_status: complete_status })
    else:    
        if recipient == "ManagerAgent":
            task = activetasks.get(task_id)
            if task is not None:  
                manageragentmessages.append({'task_id': task_id, 'message': message, 'complete': complete_status})

@app.route("/buddychat", methods=["POST"])
def chatwithhuman():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    print(f"buddy said: {data}")
    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400
    if user == 'ManagerAgent':
        chat_id = data.get('chat_id')
        task_id = data.get(task_id)
        task = activetasks.get(task_id)
        if task is not None:  
            manageragentmessages.append({'sender': 'Buddy', 'chat_id': chat_id, 'message': message, 'task_id': task_id, 'complete_status': 'False', 'chat_type': 'user'})
    else:
        chat_id = data.get('chat_id')
        # Find the chat in the chats list and add the AI's response
        chat = chats.get(chat_id)
        if chat is not None:
            # Add the AI's response to the messages list
            chat['messages'].append({'user': 'Buddy', 'message': message})
        else:
            print(f'Chat not found for {chat_id}')
            return jsonify({'status': 'failure', 'error': 'Chat not found'}), 404
    return jsonify({'status': 'success', 'message': 'Message received'}), 200



@app.route("/replytotask", methods=["POST"])
def reply_to_task():
    data = request.get_json()
    task_id = data.get('task_id')
    chat_id = data.get('chat_id')
    user_reply = data.get('reply')
    user = data.get('user')
    manageragentmessages.append({'task_id': task_id, 'chat_id': chat_id, 'user': user, 'message': user_reply, 'complete_status': 'True'})
    # Implement the logic to handle the task reply
    # For instance, updating the task status, sending it to the appropriate manager, etc.
    return jsonify({'status': 'success', 'message': 'Reply received'}), 200

def run_server():
    app.run(port=5000)  # Run the Flask app on port 5000

    
if __name__ == "__main__":
    run_server()