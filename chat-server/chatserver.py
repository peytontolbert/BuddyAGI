from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS, cross_origin
import json
import threading
import time
import uuid
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import requests
from diffusers import StableDiffusionImg2ImgPipeline, AutoPipelineForImage2Image, StableDiffusionLatentUpscalePipeline, StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers.utils import load_image
import torch
import os


# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'])
database_agentmessages = []
helpermessages = []
manageragentmessages = []
chats = {}
activetasks = {}
activeunreadtasks = {}
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

@app.route('/imager')
def imagerpage():
    return render_template('imager.html')

@app.route('/chatassistant')
def chatassistantpage():
    return render_template('chatassistant.html')

@app.route("/pinghelper", methods=["POST"])
def pinghelperagent():
    # Get message from POST request
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    chat_id = data.get('chat_id')
    print(message)
    print(user)
    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400
    # Find or create the chat in the chats list
    chat = chats.get(chat_id)
    if chat is None:
        # Create a new chat if not found
        chat = {chat_id: {'user': user, 'messages': [message], 'last_reply': 'user', 'read': False}}
        print(f"new chat: {chat}")
        chats[chat_id] = chat
    # Add the message to the messages list
    else:
        chats[chat_id]['messages'].append({'user': user, 'message': message})
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

    for chat in chats:  # Iterate over chat objects
        if chat:
            print("helper chat:")
            print(chat)
            chatlog = chats[chat]
            print("chatlog")
            print(chatlog)
            if chatlog[chat].get('read') is False:
                print(f'unread chat: {chat}')
                unread_chats.append(chatlog)
                chatlog[chat]['read'] = True  # Mark as read

    if not unread_chats:
        print('No unread messages')
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


@app.route("/managermessages", methods=["GET"])
def managermessagess():
    # Check if there are no messages
    if len(activeunreadtasks) == 0:
        return jsonify({'error': 'No messages'}), 404

    # Return all messages
    unread_tasks = activeunreadtasks.copy()  # Copy the messages
    # Clear the messages list
    activetasks.update(unread_tasks)
    activeunreadtasks.clear()

    return jsonify({'message': unread_tasks}), 200


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
    print(chat)
    print(user)
    if chat is not None:
        activetasks = chat.get('activetasks')
        messages = chat[chat_id].get('messages')
        print(f" messages: {messages}")
        if activetasks is not None:
            task_id = chat['task_id']
            task_info = activetasks.get(task_id)
            if task_info is not None:
            
            # Return the messages for this chat
                return jsonify({'messages': chat['messages'], 'activetask': task_info}), 200
            else:
                completed_task_info = completedtasks.get(chat_id)
                if completed_task_info is not None:
                    return jsonify({'messages': chat['messages'], 'completedtasks': completed_task_info, 'activetask': task_info}), 200
        else:
            if messages is not None:
                print(messages)
                return jsonify({'messages': messages}), 200
            else:
                return jsonify({'message': 'No messages'}), 404
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
    chat = chats.get(chat_id)
    task_id = chat['activetask']
    task_info = {'task_id': task_id, 'user': user, 'messages': messages, 'chat_id': chat_id}
    activeunreadtasks[task_id] = task_info
    chat = chats.get(chat_id)
    chat['messages'].append({'user': user, 'message': message, 'task_id': task_id})
    chats[chat_id] = chat
    return jsonify({'task_id': task_id}), 200

@app.route("/assigntask", methods=["POST"])
def assigntaskk():
    data = request.get_json()
    task_id = data.get('task_id')
    activetask = activetasks.get(task_id)
    chat_id = activetask['chat_id']
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
            message_list.append({'task_id': task_id, 'chat_id': chat_id, 'user': user, 'message': task})
        elif receiver == user:
            # For user, add the task message to the chat
            chat['messages'].append({'user': user, 'message': task, 'task': {'task_id': task_id, 'require_reply': True, 'complete_status': False}})
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
        helpermessages.append({'task_id': task_id, 'message': message, 'chat_type': 'agent', complete_status: complete_status })
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
    user = data.get('receiver')
    chat_id = data.get('chat_id')
    print(f"buddy said: {data}")
    # Check if the message is empty
    if not message:
        return jsonify({'status': 'failure', 'error': 'Empty message'}), 400
    # Find the chat in the chats list and add the AI's response
    chat = chats.get(chat_id)
    print(f"buddy chatted to: {chat}")
    if chat is not None:
        # Add the AI's response to the messages list
        chat[chat_id]['messages'].append({'user': 'Buddy', 'message': message})
    else:
        print(f'Chat not found for {chat_id}')
        return jsonify({'status': 'failure', 'error': 'Chat not found'}), 404
    return jsonify({'status': 'success', 'message': 'Message received'}), 200


@app.route("/completetask", methods=["POST"])
def taskcompletion():
    data = request.get_json()
    message = data.get('message')
    user = data.get('user')
    task_id = data.get('task_id')
    chat_id = data.get('chat_id')
    sender = data.get('sender')
    chat = chats.get(chat_id)
    active_task = activetasks.get(task_id)
    #move active_task to completed_task
    if active_task is not None and chat is not None:
        completedtasks[task_id] = active_task
        del activetasks[task_id]
        # Determine the receiver and append task message to the respective list
        if user.lower() in ['codingagent', 'dbagent']:
            # For coding or database agent, append to their respective message lists
            message_list = coding_agentmessages if user.lower() == 'codingagent' else database_agentmessages
            message_list.append({'task_id': task_id, 'chat_id': chat_id, 'user': user, 'message': message, 'complete_status': 'True'})
        elif user == 'Manager':
            # For user, add the task message to the chat
            chat['messages'].append({'user': user, 'message': message, 'task': {'task_id': task_id, 'require_reply': False, 'complete_status': 'True'}})
            chats[chat_id] = chat


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



@app.route('/process', methods=['POST'])
def process_image():
    # Receive the image
    file = request.files['image']
    prompt = request.form['prompt']
    strength = request.form['slider']
    img = Image.open(file.stream).convert("RGB")
    #img = preprocess_image(img)
    # Run the tile model and upscale model
    processed_image = run_tile_pipeline(img, prompt, strength)

    # Save the processed image temporarily
    processed_image.save("temp_processed.png")

    # Return the processed image
    return send_file("temp_processed.png", mimetype='image/png')

def get_low_res_img(url, shape):
    response = requests.get(url)
    shape = (200, 128)
    low_res_img = Image.open(BytesIO(response.content)).convert("RGB")
    low_res_img = low_res_img.resize(shape)
    return low_res_img


def preprocess_image(image):
    # Resize if any dimension is larger than 2000 pixels
    max_size = 2000
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size))

    # Split the image in half (you can choose between horizontal or vertical split)
    # Example for horizontal split:
    width, height = image.size
    image = image.crop((0, 0, width, height // 2))  # Adjust this line for different types of splits

    return image


def run_tile_model(generator, image, prompt, strength):
    np_image = np.array(image)
    np_image = cv2.Canny(np_image, 50, 100)
    np_image = np_image[:, :, None]
    np_image = np.concatenate([np_image, np_image, np_image], axis=2)
    canny_image = Image.fromarray(np_image)
    controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11f1e_sd15_tile", torch_dtype=torch.float16)
    model_directory = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(model_directory, controlnet=controlnet, torch_dtype=torch.float16,
    safety_checker = None,
    requires_safety_checker = False)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    image = pipe(
                prompt=prompt,
                num_inference_steps=45,
                strength=strength,
                generator=generator,
                image=image,
                control_image=image,
).images[0]
    return image


def run_tile_pipeline(image, prompt, strength):
    generator = torch.manual_seed(0)
    # Pre-process: Resize if necessary and split
    # prompt = "high resolution, realism, clear quality, masterpiece, sharply defined, 32k quality"
    if prompt is not None and image is not None and strength is not None:
        new_image = run_tile_model(generator, image, prompt, strength)
        return new_image
    return None


def run_server():
    app.run(port=5000)  # Run the Flask app on port 5000

    
if __name__ == "__main__":
    run_server()