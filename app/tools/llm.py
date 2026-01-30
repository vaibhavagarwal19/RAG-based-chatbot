from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.2
)
