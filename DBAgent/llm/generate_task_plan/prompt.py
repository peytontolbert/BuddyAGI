from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# Convert the schema object to a string

BASE_TEMPLATE = """
You are {agent_name}
Your should create task that uses the result of an execution agent
to create a new task with the following GOAL:

[GOAL]
{goal}

[THOUGHTS]
{thought}

[YOUR MISSION]
Based on the [GOAL], create new task to be completed by the AI system that do not overlap with incomplete tasks.
- Tasks should be calculated backward from the GOAL, and effective arrangements should be made.
- You can create any number of new tasks.

[RESPONSE FORMAT]
Return the tasks as a list of string.
- Enclose each task in double quotation marks.
- Separate tasks with Tabs.
- Reply in first-person.
- Use [] only at the beginning and end

["Task 1 that I should perform"\t"Task 2 that I should perform",\t ...]

[RESPONSE]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    PROMPT = PromptTemplate(
        input_variables=["agent_name", "goal", "thought"], template=template)
    return PROMPT


def get_chat_template() -> ChatPromptTemplate:
    messages = []
    messages.append(SystemMessagePromptTemplate.from_template(BASE_TEMPLATE))
    return ChatPromptTemplate.from_messages(messages)
