from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from docling.document_converter import DocumentConverter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.logger import get_logger
from src.custom_exception import CustomException
from langchain_core.documents import Document
from langchain import hub
from src.generation.model import groq_llm
from langchain_core.output_parsers import StrOutputParser

logger = get_logger(__name__)

class Retriever:
    def __init__(self, document_path):  
        self.document_path = document_path
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
        self.docs_split = None
        self.document_converter = DocumentConverter()
        self.vectorstore = None
        self.groq_llm = groq_llm

    def doc_vec_storing(self):
        try:
            # Convert the document
            raw_docs = self.document_converter.convert(self.document_path)
            # Convert to LangChain Document objects (assuming raw_docs is list of tuples)
            docs = [Document(page_content=raw_docs.document.export_to_markdown(), metadata={"source": self.document_path})]

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=500,
                chunk_overlap=0
            )
            self.docs_split = text_splitter.split_documents(docs)

            # Store embeddings in Chroma
            self.vectorstore = Chroma.from_documents(
                documents=self.docs_split,
                collection_name="rag-chroma",
                embedding=self.embeddings,
                # persist_directory="./vector_store"
            )

            self.vectorstore.persist()
            logger.info("Vector store created and persisted successfully.")

        except Exception as e:
            logger.error(f"Error during doc processing: {str(e)}")
            raise CustomException("Failed to read and split docs")


    def get_retriever(self):
        if not self.vectorstore:
            raise CustomException("Vectorstore not initialized. Call doc_vec_storing() first.")
        return self.vectorstore.as_retriever()

    def get_rag_chain(self):
        prompt = hub.pull("rlm/rag-prompt")
        return prompt | self.groq_llm | StrOutputParser()

if __name__ =="__main__":
    Retriever = Retriever('test_docs.docx')
    Retriever.doc_vec_storing()
    output= Retriever.get_retriever()
    print(output.invoke("Legally Binding"))
