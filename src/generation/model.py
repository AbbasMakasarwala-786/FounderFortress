from langchain_groq import ChatGroq
from langchain.callbacks import AsyncIteratorCallbackHandler
from dotenv import load_dotenv
load_dotenv()
callback = AsyncIteratorCallbackHandler()
groq_llm = ChatGroq(model = 'llama-3.3-70b-versatile',
                    streaming=True,
                    callbacks=[callback]
                    )
# deepseek-r1-distill-llama-70b