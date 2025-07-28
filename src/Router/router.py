from fastapi import FastAPI, UploadFile, File, Form
from fastapi.exceptions import HTTPException
from typing import AsyncIterable
from src.generation.model import callback
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# from config.path_config import * 
from langgraph.graph import END
import shutil
import os
from src.generation.graph import RAGGraph

app = FastAPI()
UPLOAD_DOC = 'data/uploaded_data'
os.makedirs(UPLOAD_DOC, exist_ok=True)

graph_registry = {}
vector_registry = {}  

# Fixed CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    # For production, use specific origins instead:
    # allow_origins=["http://localhost:3000", "https://your-production-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file.filename = file.filename.replace(" ", "_")
        file_path = os.path.join(UPLOAD_DOC, file.filename)
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        pipeline = RAGGraph(file_path)
        rag_app = pipeline.build_graph()
        
        graph_registry[file.filename] = rag_app
        vector_registry[file.filename] = pipeline  # optional, to store retriever class

        return {"doc_id": file.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")



def generate_response(doc_id: str, question: str):
    try:
        graph = graph_registry[doc_id]
        initial_state = {"question": question}
        config = {
            "configurable": {  # Fixed typo: lowercase 'c'
                "thread_id": 1
            }
        }
        
        # Stream messages and yield raw content
        for token, metadata in graph.stream(initial_state, config=config, stream_mode="messages"):
            if hasattr(token, 'content') and token.content:
                yield token.content  # Raw content - works with fetch()
    
    except Exception as e:
        yield f"Error: {str(e)}"



@app.post("/ask")
async def ask_question(doc_id: str = Form(...), question: str = Form(...)):
    try:
        if doc_id not in graph_registry:
            raise HTTPException(status_code=404, detail="Document not found")

        return StreamingResponse(
            generate_response(doc_id, question),  # Fixed function name typo
            media_type='text/plain',  # Use text/plain for simple streaming
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")
    
    
# def generate_response(doc_id: str, question: str):
#     try:
#         graph = graph_registry[doc_id]
#         initial_state = {"question": question}
#         config = {
#             "configurable": {  # Fixed typo: lowercase 'c'
#                 "thread_id": 1
#             }
#         }
        
#         # If you want to stream individual messages/tokens:
#         for event in graph.stream(initial_state, config=config, stream_mode="messages"):
#             # event is typically (node_name, message)
#             if len(event) >= 2:
#                 message = event[1]  # Get the message part
#                 if hasattr(message, 'content') and message.content:
#                     # Format as proper SSE
#                     yield f"data: {message.content}\n\n"
    
#     except Exception as e:
#         # Send error as SSE event
#         yield f"data: Error: {str(e)}\n\n"
#     finally:
#         # Send end-of-stream marker
#         yield "data: [DONE]\n\n"

# @app.post("/ask")
# async def ask_question(doc_id: str = Form(...), question: str = Form(...)):
#     try:
#         if doc_id not in graph_registry:
#             raise HTTPException(status_code=404, detail="Document not found")

#         return StreamingResponse(
#             generate_response(doc_id, question),  # Fixed function name typo
#             media_type='text/plain',  # Use text/plain for SSE
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "Content-Type": "text/event-stream",  # Explicitly set SSE content type
#             }
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

# Optional: Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}