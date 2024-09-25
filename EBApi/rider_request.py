from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from .prompts import SYSTEM_PROMPT, EBIKES_INFO, RIDERS_PROMPT, RIDERS_ACCEPTANCE_PROMPT, DELIVERY_COMPLETION_PROMPT
from .gpt_model import model


def get_riders_prompt_template():
    """Template for interactions with riders"""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.format(ebikes_info=EBIKES_INFO)),
        MessagesPlaceholder(variable_name="conversation_history"),
        ("user", "{input}"),
        ("assistant", RIDERS_PROMPT)
    ])


def create_riders_chain():
    """Define chain with the LLM, memory and prompt template"""
    prompt_template = get_riders_prompt_template()
    chain = prompt_template | model | StrOutputParser()
    return chain


def get_riders_acceptance_prompt_template():
    """Template for rider accepting delivery request"""
    class Acceptance(BaseModel):
        acceptance: str = Field(description="Rider acceptance to delivery request returning 'Yes' or 'No'")
        phone_number: str = Field(description="Client phone number")
        order_id: str = Field(description='Order Id')

    json_parser = JsonOutputParser(pydantic_object=Acceptance)
    format_instructions = json_parser.get_format_instructions()

    prompt_template = PromptTemplate(
        template=RIDERS_ACCEPTANCE_PROMPT,
        input_variables=["input", "announcement"],
        partial_variables={"format_instructions": format_instructions}
    )

    return prompt_template, json_parser


def create_riders_acceptance_chain():
    """Define chain for returning yes or no when rider accepts an order"""
    prompt_template, json_parser = get_riders_acceptance_prompt_template()
    chain = prompt_template | model | json_parser
    return chain


def get_delivery_completion_template():
    """Template for rider delivery completions"""
    class Completion(BaseModel):
        completed: str = Field(description="Rider acceptance to delivery request returning 'Yes' or 'No'")

    json_parser = JsonOutputParser(pydantic_object=Completion)
    format_instructions = json_parser.get_format_instructions()

    prompt_template = PromptTemplate(
        template=DELIVERY_COMPLETION_PROMPT,
        input_variables=["input", "conversation_history"],
        partial_variables={"format_instructions": format_instructions}
    )

    return prompt_template


def create_delivery_completion_chain():
    """Define chain for delivery completions"""
    prompt_template = get_delivery_completion_template()
    chain = prompt_template | model | JsonOutputParser()
    return chain


riders_chain = create_riders_chain()
riders_acceptance_chain = create_riders_acceptance_chain()
delivery_completion_chain = create_delivery_completion_chain()
