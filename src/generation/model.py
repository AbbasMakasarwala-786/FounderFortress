from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

groq_llm = ChatGroq(model = 'qwen-qwq-32b')