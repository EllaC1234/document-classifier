import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import router

# Configure logging
def setup_logging():
    os.makedirs(settings.LOGS_DIRECTORY, exist_ok=True)
    log_file_path = os.path.join(settings.LOGS_DIRECTORY, "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

def create_app() -> FastAPI:
    app = FastAPI()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create required directories
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    
    # Include routers
    app.include_router(router, prefix="/api")
    
    return app

setup_logging()
app = create_app()
