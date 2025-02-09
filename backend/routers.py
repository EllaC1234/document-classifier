from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from config import settings
from ml_service import MLService
from document_handler import DocumentHandler
from database_model import get_db
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)
ml_service = MLService()

class UploadResponse(BaseModel):
    filename: str
    predictions: List[dict]

class GetDocumentResponse(BaseModel):
    id: int
    filename: str
    category: str
    confidence: str
    upload_time: str

@router.post("/upload", 
    status_code=201,
    response_model=UploadResponse,
    summary="Upload and classify a document",
    description="Upload a text document and get its classification predictions"
)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and classify a document.

    Parameters:
    - file: Text file to be uploaded and classified
    
    Returns:
    - filename: Name of the uploaded file
    - predictions: List of classification predictions with confidence scores
    
    Raises:
    - 400: If file encoding is invalid
    - 500: If server encounters an error during processing
    """
    try:
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        try:
            text_content = contents.decode("utf-8")
        except Exception as e:
            logger.error(f"Error decoding file {file.filename}: {e}")
            raise HTTPException(status_code=400, detail="Invalid file encoding")
        
        classification_result = ml_service.classify_document(text_content)
        
        repo = DocumentHandler(db)
        doc = repo.create_document(
            filename=file.filename,
            file_path=file_path,
            content=text_content,
            category=classification_result['category'],
            confidence=str(classification_result['predictions'][0]['confidence'])
        )
        
        return {
            "filename": doc.filename,
            "predictions": classification_result['predictions']
        }
    except Exception as e:
        logger.exception(f"Error processing upload: {e}")
        try:
            os.remove(file_path)
        except OSError as e:
                logger.warning(f"Failed to delete file after unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_documents",
    response_model=List[GetDocumentResponse],
    summary="Get all documents",
    description="Retrieve a list of all previously classified documents"
)
def get_documents(db: Session = Depends(get_db)):
    """
    Retrieve all classified documents.

    Returns:
    - List of documents with their classifications and metadata
    
    Each document contains:
    - id: Unique identifier
    - filename: Name of the document
    - category: Assigned classification category
    - confidence: Classification confidence score
    - upload_time: Time when document was uploaded
    """
    repo = DocumentHandler(db)
    documents = repo.get_all_documents()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "category": doc.category,
            "confidence": doc.confidence,
            "upload_time": doc.upload_time
        } 
        for doc in documents
    ]