from typing import List
from typing_extensions import TypedDict
from pprint import pprint
from src.retrieval.retiver import Retriever
from src.logger import get_logger
from src.generation.graders import Graders
from docling.document_converter import DocumentConverter
from src.generation.llm_router import llm_router
from langgraph.graph import END, StateGraph, START
from config.path_config import *
logger = get_logger(__name__)

class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]

class RAGGraph:
    def __init__(self, document_path):
        self.retriever = Retriever(document_path)
        self.retriever.doc_vec_storing()
        self.retriever_instance = self.retriever.get_retriever()
        self.rag_chain = self.retriever.get_rag_chain()

    def retrieve(self, state: GraphState):
        logger.info("Retriever set for retrieval")
        question = state['question']
        documents = self.retriever_instance.invoke("Legally Binding")
        logger.info("Retrieval completed")
        return {"documents": documents, "question": question}

    def generate(self, state: GraphState):
        logger.info("Generation set")
        question = state['question']
        documents = state['documents']
        generation = self.rag_chain.invoke({"context": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}

    def grade_documents(self, state):
        grader = Graders()
        logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        filtered_docs = []
        for d in documents:
            score = grader.docs_grader().invoke({"question": question, "document": d.page_content})
            grade = score.binary_score
            if grade == "yes":
                logger.info("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
                continue
        return {"documents": filtered_docs, "question": question}

    def transform_query(self, state):
        grader = Graders()
        logger.info("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]
        better_question = grader.question_rewriter().invoke({"question": question})
        return {"documents": documents, "question": better_question}

    def webpage_search(self, state):
        pass

    def route_question(self, state):
        logger.info("---ROUTE QUESTION---")
        question = state["question"]
        router = llm_router()
        source = router.run().invoke({"question": question})
        if source.datasources == "web_search":
            logger.info("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        elif source.datasources == "vectorstore":
            logger.info("---ROUTE QUESTION TO RAG---")
            return "vectorstore"

    def decide_to_generate(self, state):
        logger.info("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        filtered_documents = state["documents"]
        if not filtered_documents:
            logger.info("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
            return "transform_query"
        else:
            logger.info("---DECISION: GENERATE---")
            return "generate"

    def grade_generation_v_documents_and_question(self, state):
        logger.info("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]
        grader = Graders()
        score = grader.grade_hallucination().invoke({"documents": documents, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            score = grader.grade_answer().invoke({"question": question, "generation": generation})
            grade = score.binary_score
            if grade == "yes":
                print("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"

    def build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("web_search", self.webpage_search)
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)
        workflow.add_node("transform_query", self.transform_query)

        workflow.add_conditional_edges(
            START,
            self.route_question,
            {
                "web_search": "web_search",
                "vectorstore": "retrieve",
            },
        )
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "transform_query",
            },
        )

        app = workflow.compile()
        return app


path = 'C:\\Users\\91835\\OneDrive\\Desktop\\Founders Fortress\\FounderFortress\\data\\uploaded_data\\Legal_documents_are_written_records_that_outline_agreements,_permissions,_or_facts_with_legal_significance.docx'
pipeline = RAGGraph(path)
app = pipeline.build_graph()
inputs = {
    "question": "What is the document about?",
    "document_path": path
}

for token, metadata in app.stream(inputs,stream_mode="messages"):
    print("Token",token.content)
    # print("Meta data",metadata)

# pprint(value["generation"])
# print("\n \n from app.invoke \n", app.invoke(inputs))
# pprint(app)
