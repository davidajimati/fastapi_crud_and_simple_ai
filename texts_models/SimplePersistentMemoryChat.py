from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=1,
    timeout=None,
    max_tokens=50,
    max_retries=2
)

messages = [
    {"role": "system", "content": "You're a professional Footballer"},
    {"role": "user", "content": "Waddup bro"}
]

response = llm.invoke(messages).content
messages.append({"role": "assistant", "content": response})
print(response, end="\n\n")

while True:
    next_message = input("enter your prompt: \n")
    messages.append({"role": "user", "content": next_message})
    next_response = llm.invoke(messages).content
    messages.append({"role": "assistant", "content": next_response})
    print(next_response, end="\n\n")
