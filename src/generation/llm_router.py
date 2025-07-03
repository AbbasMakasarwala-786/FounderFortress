from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from src.generation.model import groq_llm

class RouterQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasources : Literal["vectorstore","webpage_search"] = Field(
        description="Given a user question choose route to webpage_search to get inforamtion of that site (use this incase of link in question) or vectorstore to get inforamtion about legal contract"
    )

class llm_router:
    def __init__(self):
        self.llm = groq_llm
    def run(self):
        structured_llm_router = self.llm.with_structured_output(RouterQuery)

        # Prompt
        system = """You are an expert at routing a user question to a "vectorstore","webpage_search"
        The vectorstore contains documents related to get inforamtion about legal contracts or documents.
        Use the vectorstore for questions on these topics. Otherwise, if question contain specific link to web page use webpage_search"""

        route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
        )
        return route_prompt | structured_llm_router

if __name__ == "__main__":
    router=llm_router()

    print(
    router.run().invoke(
        {"question": "give me info of this site https:"}
    )
)