import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, ChatResponse, HealthResponse
from app.catalog_store import CatalogStore
from app.catalog_retriever import CatalogRetriever
from app.agent import SHLAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing catalog and ML model instances...")
catalog_store = CatalogStore()
retriever = CatalogRetriever(catalog_store)
agent = SHLAgent(catalog_store, retriever)
logger.info("Started !!!!!")

app = FastAPI(title="SHL Assessment api endpointsss")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages array cannot be empty")

        response = agent.process(request.messages)
        return response
    except HTTPException as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error -> Please retry in a while")