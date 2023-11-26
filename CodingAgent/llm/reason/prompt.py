# flake8: noqa
import json
import time
from langchain.prompts import PromptTemplate
from pydantic import Field
from typing import List
from memory.episodic_memory import Episode
from llm.reason.schema import JsonSchema
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)




BASE_TEMPLATE = """
Your decisions are made to make independent actions as an autonomous coding agent.


[PERFORMANCE EVALUATION]
1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.
2. Constructively self-criticize your tasks and actions to improve your performance.
3. Reflect on past decisions and strategies to refine your approach.

[RELATED PAST EPISODES]
This reminds you of related past events:
{related_past_episodes}


[YOUR TASK]
You are given the following task:
{task}

[TOOLS]
Available tools for this task are listed below. You can use ONLY ONE TOOL at a time.
{tool_info}
"""

RECENT_EPISODES_TEMPLETE = """
[RECENT EPISODES]
This reminds you of recent events:
"""

SCHEMA_TEMPLATE = """
[RULE]
Your response must be provided exclusively in the JSON format outlined below, without any exceptions. 
Any additional text, explanations, or apologies outside of the JSON structure will not be accepted. 
Please ensure the response adheres to the specified format and can be successfully parsed by Python's json.loads function.

Strictly adhere to this JSON RESPONSE FORMAT for your response:
Failure to comply with this format will result in an invalid response. 
Please ensure your output strictly follows JSON RESPONSE FORMAT.

[JSON RESPONSE FORMAT]
{{
    "observation": "Your observation of recent episodes and their relevance to the current task.",
    "thoughts": {{
        "task": "Your understanding of the task assigned to you.",
        "past_events": "Key points from past events that help in this task.",
        "idea": "Your proposed approach or idea to perform the task.",
        "reasoning": "The reasoning behind your proposed approach.",
        "criticism": "Any constructive self-criticism or considerations.",
        "summary": "A brief summary to communicate to the user."
    }},
    "action": {{
        "tool_name": "The chosen tool from the list in [TOOLS].",
        "args": {{
            "arg1": "value1",
            "arg2": "value2"
            // Additional arguments as needed
        }}
    }}
}}
Determine which next command to use, and respond using the format specified above.
"""

def get_templatechatgpt(Dicts = {}):
    print("Dicts: ", Dicts)
        # Ensure necessary keys are in Dicts
    print("required key check on Dicts")
    required_keys = ["related_past_episodes", "task", "tool_info"]
    for key in required_keys:
        if key not in Dicts:
            raise KeyError(f"The required key {key} was not found in Dicts.")

    template = BASE_TEMPLATE.format(related_past_episodes=Dicts["related_past_episodes"], task=Dicts["task"], tool_info=Dicts["tool_info"])
    return template

def add_schema_template():
    template = SCHEMA_TEMPLATE
    return template


def memory_to_template(memory: List[Episode] = None):
    # If there are past conversation logs, append them
    recent_episodes = ""
    if memory and len(memory) > 0:
        # insert current time and date
        
        recent_episodes = RECENT_EPISODES_TEMPLETE
        recent_episodes += f"The current time and date is {time.strftime('%c')}"

        # insert past conversation logs
        for episode in memory:
            thoughts_str = json.dumps(episode.thoughts)
            action_str = json.dumps(episode.action)
            result = episode.result
            recent_episodes += thoughts_str + "\n" + action_str + "\n" + result + "\n"
    return recent_episodes
 #       template += recent_episodes
 #   template += SCHEMA_TEMPLATE
 #   return template"""
