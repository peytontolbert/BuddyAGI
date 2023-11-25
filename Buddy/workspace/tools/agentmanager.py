import os
import psycopg2
import subprocess
from dotenv import load_dotenv
import requests
load_dotenv()
class AgentManager:
    def __init__(self):
        pass
    def new_conversation(self, agents, message):
        # Base URL for the requests
        base_url = 'http://localhost:5000'
        # Data to be sent in the POST request
        data = {'user': 'Buddy', 'agents': agents, 'message': message }
        response = requests.post(f'{base_url}/newchat', json=data)
        # Optional: Check response status and handle accordingly
        if response.status_code == 200:
            data = response.json()
            chat_id = data['chat_id']
            print(f"Chat started with chat_id: {chat_id}")
            return chat_id
        else:
            print(f"Failed to start a chat with: {agents}")
            return f"Failed to start a chat with: {agents}"
        
    def read_conversation(self, chat_id):
        base_url = 'http://localhost:5000'
        data = {'user': 'Buddy', 'chat_id': chat_id}
        response = requests.post(f'{base_url}/readchat', json=data)
        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
        else:
            print(f"Failed to read chat with chat_id: {chat_id}")
            return f"Failed to read chat with chat_id: {chat_id}"
        
    def write_conversation(self, chat_id, message):
        base_url = 'http://localhost:5000'
        data = {'user': 'Buddy', 'chat_id': chat_id, 'message': message}
        response = requests.post(f'{base_url}/writechat', json=data)
        if response.status_code == 200:
            print(f"Successfully wrote to chat with chat_id: {chat_id}")
            return f"Successfully wrote to chat with chat_id: {chat_id}"
        else:
            print(f"Failed to write chat with chat_id: {chat_id}")
            return f"Failed to write chat with chat_id: {chat_id}"