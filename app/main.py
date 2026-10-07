"""
app/main.py
FastAPI application entry point for AI-Powered Agriculture Crop Advisory Assistant.
Mounts API routers, configures CORS, static frontend assets, and startup indexing hooks.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config.settings import settings
from app.utils.logging import get_logger
from app.rag.retriever import case_retriever
from app.ml.model_loader import model_manager

# Import API route modules
from app.api.routes_query import router as query_router
from app.api.routes_search import router as search_router
from app.api.routes_recommendation import router as rec_router
from app.api.routes_prediction import router as pred_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_evaluation import router as eval_router
from app.api.routes_health import router as health_router

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown management."""
    logger.info("Starting AI-Powered Agriculture Crop Advisory Assistant microservice...")
    
    # Check and initialize vector retriever
    ready = case_retriever.initialize()
    if not ready:
        logger.info("Indexes not yet built on disk. Automatically constructing agricultural indexes...")
        try:
            from scripts.build_index import build_indexes
            build_indexes()
            case_retriever.initialize()
        except Exception as e:
            logger.error(f"Failed to auto-build indexes: {e}")

    # Check and load ML models
    if not model_manager.suitability_model or not model_manager.suitability_model.is_trained:
        logger.info("ML models not yet trained on disk. Automatically running training pipeline...")
        try:
            from app.ml.model_training import train_and_evaluate_models
            train_and_evaluate_models()
            model_manager.reload()
        except Exception as e:
            logger.error(f"Failed to auto-train ML models: {e}")

    logger.info("Microservice initialized and ready to serve advisory requests.")
    yield
    logger.info("Shutting down Agriculture Crop Advisory Assistant microservice.")

app = FastAPI(
    title="AI-Powered Agriculture Crop Advisory Assistant",
    description=(
        "Hybrid AI agricultural decision-support system unifying RAG, FAISS Vector Search, "
        "Lexical TF-IDF, Machine Learning Suitability and Yield Prediction, Multi-Agent Collaboration, "
        "Input/Output Guardrails, and LLM-as-a-Judge Evaluation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health_router)
app.include_router(query_router)
app.include_router(search_router)
app.include_router(rec_router)
app.include_router(pred_router)
app.include_router(analysis_router)
app.include_router(feedback_router)
app.include_router(eval_router)

# Mount frontend static directory
frontend_dir = settings.BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/login", include_in_schema=False)
    @app.get("/dashboard", include_in_schema=False)
    def serve_index():
        return FileResponse(frontend_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
