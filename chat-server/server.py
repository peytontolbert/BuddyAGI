from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
import json
import threading
# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'])
messages = []
chatbox = []
unreaddm = []
finndm = []
buddydm = []
buddymessages = []
dbagentmessages = []
helpermessages = []
creatordm = []
nuggetchatbox = []
oldmessages = []
chats = []
# Function to save messages to a JSON file
def save_messages():
    # Create a lock to synchronize access to the messages list
    with app.app_context():
        data = {
            'messages': messages,
            'chatbox': chatbox,
            'nuggetchatbox': nuggetchatbox,
            'unreaddm': unreaddm,
            'buddydm': buddydm,
            'dbagentmessages': dbagentmessages,
            'helpermessages': helpermessages,
            'creatordm': creatordm,
            'oldmessages': oldmessages
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

@app.route("/privatechat", methods=["POST"])
@cross_origin()
def privatechat():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')

    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    nuggetchatbox.append({'user': user, 'message': message})
    return jsonify({'status': 'success', 'message': 'AI Message received'}), 200

@app.route("/nuggetchat", methods=["POST"])
@cross_origin()
def nuggetchat():
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')
    print(user)
    print(message)
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400
    
    nuggetchatbox.append({'user': user, 'message': message})
    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/nuggetchat", methods=["GET"])
def nuggetgetchat():
    # Check if there are no messages
    if len(nuggetchatbox) == 0:
        return jsonify({'message': 'No messages'}), 404
    message = nuggetchatbox.copy()
    nuggetchatbox.clear()
    # Return all messages
    return jsonify({'messages': message}), 200

@app.route("/messagetobuddy", methods=["POST"])
def messagetobuddy2():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    print(message)

    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    # Add the message to the messages list
    buddydm.append({'user':user, 'message': message})
    unreaddm.append({'user':user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/messagetocreator", methods=["POST"])
def messagetocreator():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    print(message)

    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    # Add the message to the messages list
    creatordm.append({'user': user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200
@app.route("/pingbuddy", methods=["POST"])
def pingbuddy():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    print(message)

    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    # Add the message to the messages list
    buddymessages.append({'user': user, 'message': message})

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
    dbagentmessages.append({'user': user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200

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
    chat = next((c for c in chats if c['chat_id'] == chat_id), None)
    if chat is None:
        # Create a new chat if not found
        chat = {'chat_id': chat_id, 'user': user, 'messages': []}
        chats.append(chat)
    # Add the message to the messages list
    chat['messages'].append({'user': user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/chat", methods=["GET"])
def chat():
    # Check if there are no messages
    if len(chatbox) == 0:
        return jsonify({'message': 'No messages'}), 404

    # Return all messages
    return jsonify({'messages': chatbox[-5:]}), 200

@app.route("/chat", methods=["POST"])
def postchatbox():
    # Get message from POST request
    data = request.get_json()
    user = data.get('user')
    message = data.get('message')
    print(user, message)

    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400

    # Add the message to the chatbox list
    chatbox.append({'user': user, 'message': message})

    return jsonify({'status': 'success', 'message': 'Message received'}), 200

@app.route("/creatordm", methods=["GET"])
def creatordms():
    # Check if there are no messages
    if len(creatordm) == 0:
        return jsonify({'message': 'No messages'}), 404

    # Return all messages
    return jsonify({'messages': creatordm}), 200



@app.route("/buddydm", methods=["GET"])
def buddydms():
    # Check if there are no messages
    if len(buddydm) == 0:
        return jsonify({'message': 'No messages'}), 404

    # Return all messages
    all_messages = buddydm.copy()  # Copy the messages
    oldmessages.append(all_messages)
    
    # Clear the messages list
    buddydm.clear()
    unreaddm.clear()

    return jsonify({'message': all_messages[-3:]}), 200

@app.route("/finndm", methods=["GET"])
def finndms():
    # Check if there are no messages
    if len(finndm) == 0:
        return jsonify({'message': 'No messages'}), 404

    # Return all messages
    all_messages = finndm.copy()  # Copy the messages
    oldmessages.append(all_messages)
    # Clear the messages list
    finndm.clear()
    unreaddm.clear()

    return jsonify({'message': all_messages[-3:]}), 200


@app.route("/buddymessages", methods=["GET"])
def buddymessagess():
    # Check if there are no messages
    if len(buddymessages) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    all_messages = buddymessages.copy()  # Copy the messages
    oldmessages.append(all_messages)
    # Clear the messages list
    buddymessages.clear()

    return jsonify({'message': all_messages[-3:]}), 200



@app.route("/dbagentmessages", methods=["GET"])
def dbagentmessagess():
    # Check if there are no messages
    if len(dbagentmessages) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    all_messages = dbagentmessages.copy()  # Copy the messages
    oldmessages.append(all_messages)
    # Clear the messages list
    dbagentmessages.clear()

    return jsonify({'message': all_messages[-3:]}), 200




@app.route("/helpermessages", methods=["GET"])
def helpermessagess():
    # Check if there are no messages
    if len(helpermessages) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    all_messages = helpermessages.copy()  # Copy the messages
    oldmessages.append(all_messages)
    # Clear the messages list
    helpermessages.clear()

    return jsonify({'message': all_messages[-3:]}), 200



@app.route("/readdms", methods=["GET"])
def olddms():
    # Check if there are no messages
    if len(oldmessages) == 0:
        return jsonify({'status': 'failure', 'error': 'No messages'}), 404

    # Return all messages
    all_messages = oldmessages.copy()  # Copy the messages
    

    return jsonify({'message': all_messages}), 200



def run_server():
    app.run(port=5000)  # Run the Flask app on port 5000

    
if __name__ == "__main__":
    run_server()