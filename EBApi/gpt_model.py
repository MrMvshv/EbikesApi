from langchain_openai import ChatOpenAI
import os


def get_model():
    llm_model = 'gpt-4o-mini'
    model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=llm_model, temperature=0.4)
    return model

model = get_model()