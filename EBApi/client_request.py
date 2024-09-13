from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from .prompts import SYSTEM_PROMPT, EBIKES_INFO, CLIENT_PROMPT, LOCATION_PROMPT
from .gpt_model import model


def get_client_prompt_template():
    """Template for interactions with clients"""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.format(ebikes_info=EBIKES_INFO)),
        MessagesPlaceholder(variable_name="conversation_history"),
        ("user", "{input}"),
        ("assistant", CLIENT_PROMPT)
    ])


def create_client_chain():
    """Define chain with the LLM, memory and prompt template"""
    prompt_template = get_client_prompt_template()
    chain = prompt_template | model | StrOutputParser()
    return chain


def get_location_prompt_template():
    """Template for parsing locations as JSON"""
    class Location(BaseModel):
        pickup_location: str = Field(description="Client pick-up location")
        dropoff_location: str = Field(description="Client drop-off location")

    json_parser = JsonOutputParser(pydantic_object=Location)
    format_instructions = json_parser.get_format_instructions()

    prompt_template = PromptTemplate(
        template=LOCATION_PROMPT,
        input_variables=["conversation_history"],
        partial_variables={"format_instructions": format_instructions}
    )

    return prompt_template, json_parser


def create_location_chain():
    """Define chain for returning locations in json format"""
    prompt_template, json_parser = get_location_prompt_template()
    chain = prompt_template | model | json_parser
    return chain


client_chain = create_client_chain()
location_chain = create_location_chain()