import requests
import openai
import time
import llm.reason.prompt as ReasonPrompt
from memory.episodic_memory import EpisodicMemory, Episode
from memory.procedural_memory import ProceduralMemory
from memory.memory import MemoryManager
from gpt.chatgpt import ChatGPT
from typing import Dict, Any, Optional, Union, List
import os
import json
from dotenv import load_dotenv
import logging
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
class Manager:
    def __init__(self, agent_classes: List[Any]):
        self.gpt = ChatGPT()  # Initialize ChatGPT
        self.episodic_memory = EpisodicMemory()
        self.procedural_memory = ProceduralMemory()
        self.memory_manager = MemoryManager(self.gpt)
        self.messages = []
        self.tasks = {}
        self.project_manager = ProjectManager(self)
        self.agents = [agent_class(self) for agent_class in agent_classes]
        pass
    def handle_new_message(self, user_message: Dict[str, Any]) -> None:
        sender, messages, task_id, chat_id, user, completed = self.parse_message(user_message)
        if task_id in self.tasks:
                if completed == True:
                    #delegate next subtask
                    self.project_manager.notify_subtask_completion(task_id, self.tasks[task_id]["current_subtask_index"])
                else:
                    #handle incomplete status messages
                    self.redirect_subtask(self, task_id, messages)
        else:
            if sender == "Buddy":
                self.assign_task(messages, task_id, chat_id, user)
            else:
                print("unknown message with no task id")
    def parse_message(self, message):
        data = json.loads(message)
        task_id = data.get("task_id")
        chat_id = data.get("chat_id")
        sender = data.get("sender")
        user = data.get("user")
        messages = data.get("messages")
        return sender, messages, task_id, chat_id, user
    def assign_task(self, chatmessages, task_id, chat_id, user):
        self.tasks[task_id] = {
                "user": user,
                "chat_id": chat_id,
                "messages": chatmessages,
                "status": "Under review by Project Manager",
                "sub_tasks": []
            }
        self.project_manager.review_new_task(task_id, self.tasks[task_id])
    def redirect_subtask(self, task_id, task):
        self.project_manager.review_subtask_redirection(task_id, task)
    def get_manager_by_name(self, name):
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    def save_agent(self) -> None:
        episodic_memory_dir = f"{self.dir}/episodic_memory"
        filename = f"{self.dir}/agent_data.json"
        self.episodic_memory.save_local(path=episodic_memory_dir)

        data = {"name": self.agent_name,
                "episodic_memory": episodic_memory_dir
                }
        with open(filename, "w") as f:
            json.dump(data, f)
    def load_agent(self) -> None:
        absolute_path = self._get_absolute_path()
        if not "agent_data.json" in os.listdir(absolute_path):
            self.ui.notify("ERROR", "Agent data does not exist.", title_color="red")
        with open(os.path.join(absolute_path, "agent_data.json")) as f:
            agent_data = json.load(f)
            try:
                self.episodic_memory.load_local(agent_data["episodic_memory"])
            except Exception as e:
                self.ui.notify(
                    "ERROR", "Episodic memory data is corrupted.", title_color="RED")
                raise e
            else:
                self.ui.notify(
                    "INFO", "Episodic memory data is loaded.", title_color="GREEN")      
    def run(self):
        self.checkmessages()
        print(self.messages)
        while self.messages:
            message = self.messages.pop(0)  # Remove and return the first message
            self.handle_new_message(message)
        time.sleep(10)
    def checkmessages(self):
        try:
            response = requests.get("http://localhost:5000/managermessages")
            if response.status_code == 200:
                self.messages.append(response.text)
            else:
                print("no new messages")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    

class ProjectManager(Manager):
    def __init__(self):
        super().__init__() # Initialize Manager
        self.name = "ProjectManager"
        self.info = "I am the project manager. I help manage projects and tasks."
    def initialize_task_structure(self, task_id, subtasks):
        self.manager.tasks[task_id].update({
            "status": "Delegated to specialized managers",
            "sub_tasks": subtasks,
            "current_subtask_index": 0
        })
    def review_new_task(self, task_id, task):
        sub_tasks = self.break_down_task(task)
        if sub_tasks:
            self.initialize_task_structure(task_id, sub_tasks)
            self.assign_next_subtask(task_id)
        else:
            logging.error("No subtasks generated for task ID {}".format(task_id))
    def assign_next_subtask(self, task_id):
        task = self.manager.tasks[task_id]
        index = task["current_subtask_index"]
        if index < len(task["sub_tasks"]):
            subtask = task["sub_tasks"][index]
            if index == 0 or subtask.get("completed") == True:
                self.delegate_subtask(task_id, subtask)
            # If subtask is not completed, wait for its completion before assigning the next subtask
        else:
            logging.error(f"All subtasks for task ID {task_id} have been assigned")
    def delegate_subtask(self, task_id, subtask):
            manager_name = subtask.get("manager")
            task_details = subtask.get("subtask")
            if manager_name and task_details and manager_name in self.manager.agents:
                subtask["in_progress"] = True
                subtask["completed"] = False
                self.manager.agents[manager_name].handle_task(task_id, task_details)
            else:
                logging.error(f"Invalid manager or subtask details in {subtask}")
    def notify_subtask_completion(self, task_id, subtask_index):
        task = self.manager.tasks[task_id]
        if subtask_index < len(task["sub_tasks"]):
            subtask = task["sub_tasks"][subtask_index]
            subtask["in_progress"] = False
            subtask["completed"] = True
            task["current_subtask_index"] = subtask_index + 1
            self.assign_next_subtask(task_id)
    def review_subtask_redirection(self, task_id, task):
        # Logic to handle the redirected subtask
        # Decide whether to reassign it to another manager or break it down further
        # You can use a similar system prompt as in break_down_task to reassess and reassign the task
        reassessed_subtasks, user_interactions = self.reassess_and_break_down_task(task)
        task = self.manager.tasks[task_id]
        index = task["current_subtask_index"]
        if reassessed_subtasks:
            task["sub_tasks"][index:index] = reassessed_subtasks
        if user_interactions:
            self.handle_user_interaction(task_id, user_interactions)
        if not user_interactions:
            self.assign_next_subtask(task_id)
    def reassess_and_break_down_task(self, task):
        systemprompt = """
        You are an AI Project Manager reassessing a redirected subtask. 
        Determine if the subtask can be further broken down for specialized managers, 
        if it requires input or action from a user, or if it should be reassigned.

        Provide your response in JSON format:
        {
            "reassessed_subtasks": [
                {"manager": "CodingManager", "subtask": "description of coding subtask"},
                {"manager": "DBManager", "subtask": "description of database subtask"}
            ],
            "user_tasks": [{"task": "description of user task"}],
            "user_questions": ["Question 1", "Question 2", ...],
            "reassign": true/false
        }
        """
        template = """
        [SUBTASK]
        {task}"""
        prompt = template.format(task=task)
        messages = {"role": "system", "content": systemprompt}, {"role": "user", "content": prompt}
        result = self.gpt.chat_with_gpt3(messages)
        print(result)
        try:
            response = json.loads(result)
            reassessed_subtasks = response.get("reassessed_subtasks", [])
            user_tasks = response.get("user_tasks", [])
            user_questions = response.get("user_questions", [])
            user_interactions = user_tasks + user_questions
            return reassessed_subtasks, user_interactions
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse the response as JSON: {e}")
            return [], []

    def break_down_task(self, task):
        # Logic to break down the task into subtasks
        systemprompt = """You are an AI Project Manager.
        Your job is to take a complex task and break it down into manageable subtasks.
        You have specialized managers for coding and database tasks.
        Please break down the following task into subtasks and specify which manager should handle each subtask.
        Respond in list format with details about the subtask and the assigned manager.

        Provide your response in JSON format:
        [
            {"manager": "CodingManager", "subtask": "description of coding subtask"},
            {"manager": "DBManager", "subtask": "description of database subtask"}
        ]
        """
        template = """[TASK]
        {task}"""
        prompt = template.format(task=task)
        messages = {"role": "system", "content": systemprompt}, {"role": "user", "content": prompt}
        result = self.gpt.chat_with_gpt3(messages)
        print(result)
        try:
            subtasks = json.loads(result)
            return subtasks
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse the response as JSON: {e}")
            return []
    def handle_user_interaction(self, task_id, user_interactions):
        task = self.manager.tasks[task_id]
        user = task["user"]
        chat_id = task["chat_id"]
        for interaction in user_interactions:
            self.send_interaction_to_user(user, chat_id, task_id, interaction)
    def send_interaction_to_user(self, user, chat_id, task_id, interaction):
        url = "http://localhost:5000/assigntask"
        data = {
            "user": user,
            "chat_id": chat_id,
            "task_id": task_id,
            "task": interaction,
            "receiver": "user"
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Interaction assigned to user: {interaction}")
            else:
                print(f"Failed to assign interaction. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while assigning interaction to user: {e}")
class CodingManager(Manager):
    def __init__(self):
        super().__init__() # Initialize Manager
        self.name = "CodingManager"
        self.info = "I am the coding manager. I handle all coding related tasks."

    def assign_task_to_agent(self, task_id, actions):
        # Assign a single-shot action to the coding agent
        for action in actions:
            self.send_task_to_agent(task_id, action)

    def send_task_to_agent(self, task_id, action):
        url = "http://localhost:5000/assigntask"
        data = {
            "sender": self.name,
            "receiver": "CodingAgent",
            "task_id": task_id,
            "task": action
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Task assigned to CodingAgent: {action}")
            else:
                print(f"Failed to assign task. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while assigning task to CodingAgent: {e}")
    def review_new_task(self, task_id, task):
        print("Coding manager reviewing task")
        print(task)
        
        systemprompt = """
        You are an AI Coding Manager. You've received a subtask from the AI Project Manager. 
        Review the subtask and decide whether it's within the scope and capability of your coding team. 
        If the subtask can be executed by your team, outline the steps needed to complete it. 
        If the subtask is too complex, unclear, or requires the expertise of another manager, 
        indicate that it needs to be reassigned or further broken down by the Project Manager.

        Respond in JSON format:
        {
            "execute": true/false,
            "actions": ["action1", "action2", ...] if executable,
            "reassign": true/false if not executable
        }

        """
        template = """
        [SUBTASK]
        {task}"""
        prompt = template.format(task=task)
        messages = [{"role": "system", "content": systemprompt}, {"role": "user", "content": prompt}]
        result = self.gpt.chat_with_gpt3(messages)
        print(result)
        # Further processing of result to extract decisions and actions
        try:
            parsed_response = json.loads(result)
            if parsed_response.get("execute"):
                actions = parsed_response.get("actions", [])
                # Process actions: Assign them to CodingAgents
            elif parsed_response.get("reassign"):
                # Redirect back to ProjectManager for reassignment or further breakdown
                self.manager.redirect_subtask(task_id, task)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse the AI response as JSON: {e}")

    def handle_task(self, task_id, task):
        self.review_new_task(task_id, task)

class DBManager(Manager):
    def __init__(self):
        super().__init__() # Initialize Manager
        self.name = "DatabaseManager"
        self.info = "I am the database manager. I handle all database related tasks."        


    def handle_task(self, task_id, task):
        """
        Review the database task and decide the action to be taken.
        """
        print("Database manager reviewing task")
        print(task)
        # Implement task review and action determination logic
        actions = self.review_database_task(task_id, task)
        for action in actions:
            self.send_task_to_agent(task_id, action)

    def review_database_task(self, task_id, task):
        """
        Review the given database task and determine the actions required.
        Respond with a list of single-shot actions or a reassignment request.
        """
        systemprompt = """
        You are an AI Database Manager. You've received a subtask from the AI Project Manager. 
        Review the subtask and decide whether it's within the scope and capability of your database team. 
        If the subtask can be executed by your team, outline the steps needed to complete it.
        If the subtask is too complex or unclear, indicate that it needs to be reassigned or further broken down.

        Respond in JSON format:
        {
            "execute": true/false,
            "actions": ["action1", "action2", ...] if executable,
            "reassign": true/false if not executable
        }
        """
        template = f"[SUBTASK]\n{task}"
        messages = [{"role": "system", "content": systemprompt}, {"role": "user", "content": template}]
        result = self.gpt.chat_with_gpt3(messages)
        print(result)
        try:
            parsed_response = json.loads(result)
            if parsed_response.get("execute"):
                return parsed_response.get("actions", [])
            elif parsed_response.get("reassign"):
                self.manager.redirect_subtask(task_id, task)
                return []
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse the AI response as JSON: {e}")
            return []

    def send_task_to_agent(self, task_id, action):
        url = "http://localhost:5000/assigntask"
        data = {
            "sender": self.name,
            "receiver": "DatabaseAgent",
            "task_id": task_id,
            "task": action
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Task assigned to DatabaseAgent: {action}")
            else:
                print(f"Failed to assign task. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while assigning task to DatabaseAgent: {e}")
