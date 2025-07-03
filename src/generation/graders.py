### Retrieval Grader
from typing import Literal
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from src.generation.model import groq_llm
from src.retrieval.retiver import Retriever
# Data model


class Graders:
    def __init__(self):
        self.groq_llm = groq_llm
        # self.question = question
        # self.document_path = document_path
        # Retrieved = Retriever(self.document_path)
        # Retrieved.doc_vec_storing()
        # retriever= Retrieved.get_retriever()
        # self.docs = retriever.invoke(self.question)


    def docs_grader(self):
        class GradeDocuments(BaseModel):
            """Binary score for relevance check on retrieved documents."""

            binary_score: str = Field(
                description="Documents are relevant to the question, 'yes' or 'no'"
            )


        # LLM with function call
        structured_llm_grader = self.groq_llm.with_structured_output(GradeDocuments)

        # Prompt
        system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )

        retrieval_grader = grade_prompt | structured_llm_grader
        
        # doc_txt = self.docs[1].page_content
        return retrieval_grader


    def grade_hallucination(self):
        class GradeHallucinations(BaseModel):
            """Binary score for hallucination present in generation answer."""

            binary_score: str = Field(
                description="Answer is grounded in the facts, 'yes' or 'no'"
            )


        # LLM with function call
        structured_llm_grader = self.groq_llm.with_structured_output(GradeHallucinations)

        # Prompt
        system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
            Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
            ]
        )

        hallucination_grader = hallucination_prompt | structured_llm_grader
        return hallucination_grader
    

    def grade_answer(self):

        class GradeAnswer(BaseModel):
            """Binary score to assess answer addresses question."""

            binary_score: str = Field(
                description="Answer addresses the question, 'yes' or 'no'"
            )


        structured_llm_grader = self.groq_llm.with_structured_output(GradeAnswer)

        # Prompt
        system = """You are a grader assessing whether an answer addresses / resolves a question \n 
            Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
            ]
        )

        answer_grader = answer_prompt | structured_llm_grader
        return answer_grader


    def question_rewriter(self):
        # Prompt
        system = """You a question re-writer that converts an input question to a better version that is optimized \n 
            for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
        
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                ),
            ]
        )

        question_rewriter = re_write_prompt | self.groq_llm | StrOutputParser()
        return question_rewriter
    
if __name__ =="__main__":
    grade= Graders()
    print(grade.question_rewriter().invoke({"question":"what is this document about?"}))