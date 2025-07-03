# from typing import List
# from typing_extensions import TypedDict
# from pprint import pprint
# from src.retrieval.retiver import Retriever
# from src.logger import get_logger
# from src.generation.graders import Graders
# from docling.document_converter import DocumentConverter
# from llm_router import llm_router

# logger = get_logger(__name__)

# class GraphState(TypedDict):
#     question:str
#     generation:str
#     documents:List[str]
#     document_path:str



# def retreive(state:GraphState):
#     logger.info("Retriver set for retrival")
#     question = state['question']
#     Retriev = Retriever(state['document_path'])
#     Retriev.doc_vec_storing()
#     output= Retriev.get_retriever()
#     documents =output.invoke("Legally Binding")

#     logger.info("Retival completed")

#     return {"documents":documents,"question":question}

# def generate(state:GraphState):
#     logger.info("Generation set")
#     question = state['question']
#     documents = state['documents']
#     Retriev = Retriever(state['document_path'])
#     generation = Retriev.get_rag_chain().invoke({"context":documents,"question":question})
#     return {"documents": documents, "question": question, "generation": generation}



# def grade_documents(state):
#     grader = Graders()
#     logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
#     question = state["question"]
#     documents = state["documents"]

#     # Score each doc
#     filtered_docs = []
#     for d in documents:
#         score = grader.docs_grader().invoke(
#             {"question": question, "document": d.page_content}
#         )
#         grade = score.binary_score
#         if grade == "yes":
#             print("---GRADE: DOCUMENT RELEVANT---")
#             filtered_docs.append(d)
#         else:
#             print("---GRADE: DOCUMENT NOT RELEVANT---")
#             continue
#     return {"documents": filtered_docs, "question": question}


# def transform_query(state):
#     grader = Graders()

#     logger.info("---TRANSFORM QUERY---")
#     question = state["question"]
#     documents = state["documents"]

#     # Re-write question
#     better_question = grader.question_rewriter().invoke({"question": question})
#     return {"documents": documents, "question": better_question}


# def webpage_search(state):
#     pass
#     # grader = Graders()
#     # doc = DocumentConverter()
#     # logger.info("--- webpage_search---")
#     # question = state["question"]

#     # # Web search
#     # docs = grader..invoke({"query": question})
#     # web_results = "\n".join([d["content"] for d in docs])
#     # web_results = Document(page_content=web_results)

#     # return {"documents": web_results, "question": question}


# ### EDGES 

# def route_question(state):
#     logger.info("---ROUTE QUESTION---")
#     question = state["question"]

#     router = llm_router()

#     source = router.run().invoke({"question": question})

#     if source.datasources == "web_search":
#         logger.info("---ROUTE QUESTION TO WEB SEARCH---")
#         return "web_search"
#     elif source.datasources == "vectorstore":
#         logger.info("---ROUTE QUESTION TO RAG---")
#         return "vectorstore"


# def decide_to_generate(state):
#     logger.info("---ASSESS GRADED DOCUMENTS---")
#     state["question"]
#     filtered_documents = state["documents"]

#     if not filtered_documents:
#         logger.info(
#             "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
#         )
#         return "transform_query"
#     else:
#         # We have relevant documents, so generate answer
#         logger.info("---DECISION: GENERATE---")
#         return "generate"


# def grade_generation_v_documents_and_question(state):
#     logger.info("---CHECK HALLUCINATIONS---")
#     question = state["question"]
#     documents = state["documents"]
#     generation = state["generation"]

#     grader = Graders()

#     score = grader.grade_hallucination().invoke(
#         {"documents": documents, "generation": generation}
#     )
#     grade = score.binary_score

#     # Check hallucination
#     if grade == "yes":
#         logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
#         # Check question-answering
#         logger.info("---GRADE GENERATION vs QUESTION---")

#         grader =Graders()

#         score = grader.grade_answer().invoke({"question": question, "generation": generation})
#         grade = score.binary_score
#         if grade == "yes":
#             print("---DECISION: GENERATION ADDRESSES QUESTION---")
#             return "useful"
#         else:
#             print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
#             return "not useful"
#     else:
#         pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
#         return "not supported"
    

# def graph():
#     from langgraph.graph import END, StateGraph, START

#     workflow = StateGraph(GraphState)

#     # Define the nodes
#     workflow.add_node("web_search", webpage_search)  # web search
#     workflow.add_node("retrieve", retreive)  # retrieve
#     workflow.add_node("grade_documents", grade_documents)  # grade documents
#     workflow.add_node("generate", generate)  # generate
#     workflow.add_node("transform_query", transform_query)  # transform_query

#     # Build graph
#     workflow.add_conditional_edges(
#         START,
#         route_question,
#         {
#             "web_search": "web_search",
#             "vectorstore": "retrieve",
#         },
#     )
#     workflow.add_edge("web_search", "generate")
#     workflow.add_edge("retrieve", "grade_documents")
#     workflow.add_conditional_edges(
#         "grade_documents",
#         decide_to_generate,
#         {
#             "transform_query": "transform_query",
#             "generate": "generate",
#         },
#     )
#     workflow.add_edge("transform_query", "retrieve")
#     workflow.add_conditional_edges(
#         "generate",
#         grade_generation_v_documents_and_question,
#         {
#             "not supported": "generate",
#             "useful": END,
#             "not useful": "transform_query",
#         },
#     )

#     # Compile
#     app = workflow.compile()

#     return app

# app = graph()
# path = 'test_docs.docx'
# # Run
# inputs = {
#     "question": "What is Legally Binding",
#     "document_path":path
# }
# for output in app.stream(inputs):
#     for key, value in output.items():
#         pprint(f"Node '{key}':")
#     pprint("\n---\n")

# # Final generation
# pprint(value["generation"])
# print("\n \n from app.invoke \n",app.invoke(inputs))
# pprint(app)















from typing import List
from typing_extensions import TypedDict
from pprint import pprint
from src.retrieval.retiver import Retriever
from src.logger import get_logger
from src.generation.graders import Graders
from docling.document_converter import DocumentConverter
from src.generation.llm_router import llm_router
from langgraph.graph import END, StateGraph, START

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


# path = 'test_docs.docx'
# pipeline = RAGGraph(path)
# app = pipeline.build_graph()
# inputs = {
#     "question": "What is Legally Binding",
#     "document_path": path
# }

# for output in app.stream(inputs):
#     for key, value in output.items():
#         pprint(f"Node '{key}':")
#     pprint("\n---\n")

# pprint(value["generation"])
# print("\n \n from app.invoke \n", app.invoke(inputs))
# pprint(app)
