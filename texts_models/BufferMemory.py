from dotenv import load_dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationTokenBufferMemory

load_dotenv()

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=1,
    max_tokens=50,
    max_retries=2,
    timeout=3
)

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="The following is chat history between me and AI:\n{history}\nMe:{input}\nAI:"
)

memory = ConversationBufferMemory(
    return_messages=False,
    ai_prefix="AI",
    human_prefix="Me"
)

conversation = ConversationChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory
)

while True:
    ai_response = conversation.predict(input=input("enter a prompt:\n"))
    print(ai_response, end="\n")

# This didn't work properly. the model keeps talking about the history