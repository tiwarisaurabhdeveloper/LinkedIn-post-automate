from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
def load_llm():
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=GROQ_API_KEY
    )
    return llm