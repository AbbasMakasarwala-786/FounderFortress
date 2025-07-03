from fastapi import FastAPI, UploadFile, File, Form
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from langgraph.graph import END
import shutil
from config.path_config import *
import os
from src.generation.graph import RAGGraph
app = FastAPI()
os.makedirs(UPLOAD_DOC, exist_ok=True)

graph_registry = {}
vector_registry = {}  # optional
origins = [
    "http://localhost:3000",  # Example: your frontend development server
    "https://your-production-frontend.com",
    "file:///C:/Users/91835/OneDrive/Desktop/kaggle/scripts/index.html",
    "http://**"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*",origins],
    allow_credentials=True,  # Allow cookies, authorization headers, etc.
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers
    )

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file.filename = file.filename.replace(" ","_")
    file_path = os.path.join(UPLOAD_DOC, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pipeline = RAGGraph(file_path)
    rag_app = pipeline.build_graph()
    
    graph_registry[file.filename] = rag_app
    vector_registry[file.filename] = pipeline  # optional, to store retriever class

    return {"doc_id": file.filename}


@app.post("/ask")
async def ask_question(doc_id: str = Form(...), question: str = Form(...)):
    if doc_id not in graph_registry:
        raise HTTPException(status_code=404, detail="Document not found")

    graph = graph_registry[doc_id]
    initial_state = {"question": question}
    result = graph.invoke(initial_state)

    return {
        "result": result.get("generation") or result.get("answer")
    }
