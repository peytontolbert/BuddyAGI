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
        sender, messages, task_id, chat_id, user = self.parse_message(user_message)
        if task_id in self.tasks:
            self.tasks[task_id].update(messages)
        else:
            if sender == "Buddy":
                self.assign_task(messages, task_id, chat_id, user)
            else:
                print("Manager handling message from another specialized manager")
                self.receive_manager_response(task_id, messages)
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
                "status": "Under review by Project Manager"
            }
        self.project_manager.review_new_task(task_id, self.tasks[task_id])
    def redirect_subtask(self, task_id, task):
        self.project_manager.review_subtask_redirection(task_id, task)
    def get_manager_by_name(self, name):
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    def receive_manager_response(self, task_id, response):
        #Handle responses from managers
        task = self.tasks[task_id]
        taskinfo = task['task']
        systemprompt = """You are an Autonomous AI Task Manager. You have received a message from a specialized manager concerning a task.
        You must decide the next action.
        If the task is complete, the task needs to be updated to complete status.
        If the manager is asking a question to Buddy, you must forward the question to Buddy.
        If the manager is trying to communicate with another manager, you must forward the message to the correct manager.

        Afterwards you will update the task_status and send the message to the correct recipient.
        
        Reply in JSON format following the example:
        [EXAMPLE]
        {
            "next_recipient": "Buddy/agent_name",
            "questions:" ["Optional question1", "Optional question2"],
            "task": "any specific task to complete"
            "complete": "True/False"
            "task_status": "waiting response from [Buddy/agent_name]"
        }"""
        prompt = """
        [TASK]
        {taskinfo}
        [RESPONSE]
        {response}"""
        template = prompt.format(taskinfo=taskinfo, response=response)
        messages = [{"role": "system", "content": systemprompt}, {"role": "user", "content": template}]
        result = self.gpt.chat_with_gpt3(messages)
        parsed_message = json.loads(result)
        next_recipient = parsed_message.get("next_recipient")
        questions = parsed_message.get("questions", [])
        task_action = parsed_message.get("task")
        complete_status = parsed_message.get("complete", False)
        task_status = parsed_message.get("task_status")
        if complete_status:
            print("task is complete")
            self.mark_task_complete(task_id)
        else:
            self.tasks[task_id]["status"] = task_status
            self.handle_task_forwarding(next_recipient, task_id, questions, task_action)

    def handle_task_forwarding(self, next_recipient, task_id, questions, task_action):
        if next_recipient == "Buddy":
            print("forwarding message to Buddy")
            self.sendquestions(questions, next_recipient, task_id)
        else:
            print("forwarding message to another manager")
            self.forwardmessage(questions, next_recipient, task_id)
            
    def forwardmessage(self, questions, next_recipient, task_id):
            agents = self.agents
            if next_recipient in agents:
                agent = agents[next_recipient]
                agent.handlemessages(questions)
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
    def review_new_task(self, task_id, task):
        sub_tasks = self.break_down_task(task)
        if sub_tasks:
            #Update the main task status
            self.manager.tasks[task_id]["status"] = "Delegated to specialized managers"
            for subtask in sub_tasks:
                manager_name = subtask.get("manager")
                task_details = subtask.get("subtask")
                if manager_name and task_details and manager_name in self.manager.agents:
                    self.manager.agents[manager_name].handle_task(task_id, task_details) 
                else:
                    logging.error(f"Invalid manager or subtask details in {subtask}")
        else:
            logging.error("No subtasks generated for task ID {}".format(task_id))
    def review_subtask_redirection(self, task_id, task):
        # Handle the redirected subtask: reassign or further break it down
        # Logic to decide the next steps for the redirected subtask
        pass
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

                
class CodingManager(Manager):
    def __init__(self):
        super().__init__() # Initialize Manager
        self.name = "CodingManager"
        self.info = "I am the coding manager. I handle all coding related tasks."

    def review_task_assignment(self, task_info):
        # Logic to break down the task and complete it step by step
        # Ask manager any clarifying questions
        # if no questions, assign single-shot action to agent (e.g. "write a function that does X", "read a specific file", "edit a specific file", etc.)
        pass

    def assign_coding_task(self, task_info):
        # Specialized task assignment for coding tasks
        pass
    def review_code(self, code_submission):
        # Logic to review the submitted code
        pass
    def checkmessages(self):
        try:
            response = requests.get("http://localhost:5000/codingagentmessages")
            if response.status_code == 200:
                self.messages.append(response.text)
            else:
                print("no new messages")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
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
    def assign_database_task(self, task_info):
        # Specialized task assignment for database tasks
        pass
    def verify_response(self, response):
        #Logic to verify the response from the database actions
        pass
    def handletask(self, task):
        #Logic to take a task and send single shot tasks to database agent
        pass

class CodingAgent:
    def __init__(self):
        self.gpt = ChatGPT()  # Initialize ChatGPT
        self.episodic_memory = EpisodicMemory()
        self.procedural_memory = ProceduralMemory()
        self.memory_manager = MemoryManager(self.gpt)
        self.messages = []
        pass

    def sendreply(self, reply, identifier, new_task=False):
        url = "http://localhost:5000/codingreply"
        data = {"message": reply, "task_id": identifier}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("message sent")
            else:
                print("message not sent")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def handlemessages(self, message):
        related_past_episodes = self.episodic_memory.remember_related_episodes(
            message, k=3
        )
        tools = self.procedural_memory.remember_all_tools()
        tool_info = ""
        for tool in tools:
            tool_info += tool.get_tool_info() + "\n"
        Dicts = {"related_past_episodes": related_past_episodes, "task": message, "tool_info": tool_info}
        prompt = ReasonPrompt.get_templatechatgpt(
            Dicts=Dicts
        )
        schematemplate = ReasonPrompt.add_schema_template()
        prompt_messages = [{"role": "system", "content": schematemplate}, {"role": "user", "content": prompt}]
        results = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=prompt_messages)
        result = results['choices'][0]['message']['content']
        print(result)
        print("parsing message")
        parsed_message = json.loads(result)
        tool_name = parsed_message["action"]["tool_name"]
        print(f"tool_name: {tool_name}")
        args = parsed_message["action"]["args"]
        #get tool from result
        action = self.act(tool_name, args)
        print(action)
        episode = Episode(
            message=message,
            result=result,
            action=action

        )
        summary = self.episodic_memory.summarize_and_memorize_episode(episode)
        self.memory_manager.store_memory(message, result, action, summary)
        self.save_agent()
        return action

    def act(self, tool_name: str, args: Dict) -> str:
        # Get the tool to use from the procedural memory
        try:
            tool = self.procedural_memory.remember_tool_by_name(tool_name)
        except Exception as e:
            return "Invalid command: " + str(e)
        try:
            print(f"args: " + str(args))
            result = tool.run(**args)
            return result
        except Exception as e:
            return "Could not run tool: " + str(e)
    
    def generatenewtask(self, chat):
        message = chat['message']
        
        tools = self.procedural_memory.remember_all_tools()
        tool_info = ""
        for tool in tools:
            tool_info += tool.get_tool_info() + "\n"

        template = """Task Request for Autonomous Coding Agent:

As an autonomous coding agent, you have received a new task. Your first step is to thoroughly review the provided conversation or task details. After reviewing, identify and clarify any aspects that require further information or assistance.

Key Responsibilities:

Analyze the task requirements comprehensively.
Formulate questions to clarify any ambiguous or missing information.
Determine if you require support from other specialized agents, such as database or search capabilities.
Keep your responses focused on coding-related aspects and seek collaboration when the task extends beyond your scope.
Remember, your primary objective is to ensure a complete understanding of the task at hand to execute it efficiently.
available tools:
{tool_info}"""
        systemprompt = template.format(tool_info=tool_info)
        prompt_messages = [{"role": "system", "content": systemprompt}, {"role": "user", "content": message}]
        results = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=prompt_messages)
        result = results['choices'][0]['message']['content']
        return result
    


class DBAgent:
    def __init__(self):
        self.gpt = ChatGPT()  # Initialize ChatGPT
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        self.memory_manager = MemoryManager(self.gpt)
        self.messages = []
        pass

    def run(self):
        self.checkmessages()
        print(self.messages)
        while self.messages:
            result, message = self.filtermessages()
            print(result)
            if result == 'yes' or 'Yes':
                print("DB agent handling database message")
                self.handlemessages(message)
            else:
                print("message not meant for database")
        time.sleep(10)


    def checkmessages(self):
        try:
            response = requests.get("http://localhost:5000/dbagentmessages")
            if response.status_code == 200:
                self.messages.append(response.text)
            else:
                print("no new messages")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    def filtermessages(self, retries=5, delay=10):
        if not self.messages:
            print("No messages to filter.")
            return
        #get the oldest message from the self.messages list
        message = self.messages.pop(0)
        systemprompt = """Remember, your only reply should be yes or no."""
        inputprompt = """You are an AI database filter agent.
        Your task is to determine if the message is meant for tasks handling a database. 
        Reply yes or no if the follow message is meant to interact with a database:
        [MESSAGE]
        {message}"""
        chat_input = inputprompt.format(message=message)
        
        for i in range(retries):
            try:
                results = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=[{"role": "system", "content": chat_input}])
                result =  str(results['choices'][0]['message']['content'])
                return result, message
            except openai.error.ServiceUnavailableError:
                if i < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    def handlemessages(self, message):
        related_past_episodes = self.episodic_memory.remember_related_episodes(
            message, k=3
        )
        tools = self.procedural_memory.remember_all_tools()
        tool_info = ""
        for tool in tools:
            tool_info += tool.get_tool_info() + "\n"
        Dicts = {"related_past_episodes": related_past_episodes, "task": message, "tool_info": tool_info}
        prompt = ReasonPrompt.get_templatechatgpt(
            Dicts=Dicts
        )
        schematemplate = ReasonPrompt.add_schema_template()
        prompt_messages = [{"role": "system", "content": schematemplate}, {"role": "user", "content": prompt}]
        results = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=prompt_messages)
        result = results['choices'][0]['message']['content']
        print(result)
        print("parsing message")
        parsed_message = json.loads(result)

        tool_name = parsed_message["action"]["tool_name"]
        print(f"tool_name: {tool_name}")
        args = parsed_message["action"]["args"]
        #get tool from result
        action = self.act(tool_name, args)
        print(action)
        episode = Episode(
            message=message,
            result=result,
            action=action

        )
        summary = self.episodic_memory.summarize_and_memorize_episode(episode)
        self.memory_manager.store_memory(message, result, action, summary)
        self.save_agent()
        return action

    def act(self, tool_name: str, args: Dict) -> str:
        # Get the tool to use from the procedural memory
        try:
            tool = self.procedural_memory.remember_tool_by_name(tool_name)
        except Exception as e:
            return "Invalid command: " + str(e)
        try:
            print(f"args: " + str(args))
            result = tool.run(**args)
            return result
        except Exception as e:
            return "Could not run tool: " + str(e)


    def connect_to_database():
        try:
            # Connect to your PostgreSQL database. Replace these placeholders with your actual database credentials
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                port=os.getenv("PORT")
            )
            return conn
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")
            return None
                
