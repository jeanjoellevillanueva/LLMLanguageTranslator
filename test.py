import os

import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')


llm = ChatOpenAI(
    model='gpt-4',
    openai_api_key=openai_api_key
)


if __name__ == '__main__':
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    response = llm.invoke(messages)
    print(response)
