"""
this project is to test out basic agentic AI code with python
"""
import time
from asyncio import wait_for

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=1,
    max_retries=2,
    timeout=None,
    max_tokens=None
    # other params...
)

#  defining messages and invoking it manually:
messages = [
    {
        "role": "system",
        "content": "You're an helpful assistant"
    },
    {
        "role": "user",
        "content": "How are you?"
    }
]
# ai_response = llm.invoke(messages)
# print(ai_response.content)

# defining messages via langchain messages module

chat_messages = [
    SystemMessage("You're a professional translator, you respond to user input in 10 languages"),
    HumanMessage("Tell me how flat the world is in many languages")
]
# print(llm.invoke(chat_messages))®


#  using prompt template®
prompt_template = ChatPromptTemplate.from_messages([("system", "Translate this user input to {language}"), "user", "{text}"])

prompt = prompt_template.invoke({
    "language": "Yoruba",
    "text": "How old are you?"
})
# print(invoked_message.to_messages())
ai_response  = llm.invoke(prompt).content
print(ai_response)
