import json
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from llm.extract_entity.schema import JsonSchema
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)

# Convert the schema object to a string
JSON_SCHEMA_STR = json.dumps(JsonSchema.schema)

ENTITY_EXTRACTION_TEMPLATE = """
    You are an AI assistant reading a input text and trying to extract entities from it.
    Extract ONLY proper nouns from the input text and return them as a JSON object.
    You should definitely extract all names, places, functions, classes, filenames, etc.

    [INPUT TEXT]:
    {text}
    """

SCHEMA_TEMPLATE = """
    [RULE]
    Your response must be provided exclusively in the JSON format outlined below, without any exceptions. 
    Any additional text, explanations, or apologies outside of the JSON structure will not be accepted. 
    Please ensure the response adheres to the specified format and can be successfully parsed by Python's json.loads function.

    Strictly adhere to this JSON RESPONSE FORMAT for your response.
    Failure to comply with this format will result in an invalid response. 
    Please ensure your output strictly follows RESPONSE FORMAT.
    Remember not to copy the [EXAMPLE].

    [JSON RESPONSE FORMAT]
    schema = {
        "entity1": "description of entity1. Please describe the entities using sentences rather than single words.",
        "entity2": "description of entity2. Please describe the entities using sentences rather than single words.",
        "entity3": "description of entity3. Please describe the entities using sentences rather than single words."
    }

    [RESPONSE]"""


def get_template() -> PromptTemplate:
    template = f"{ENTITY_EXTRACTION_TEMPLATE}\n{SCHEMA_TEMPLATE}"
    return template


def get_chat_template() -> ChatPromptTemplate:
    messages = []
    messages.append(SystemMessagePromptTemplate.from_template(
        ENTITY_EXTRACTION_TEMPLATE))
    messages.append(SystemMessagePromptTemplate.from_template(SCHEMA_TEMPLATE))
    return ChatPromptTemplate.from_messages(messages)
