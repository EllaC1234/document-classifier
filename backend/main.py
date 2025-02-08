from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database_model import *
from transformers import pipeline
import datetime, os
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Your Angular app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],
)

# ML Model Loading (Hugging Face)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ["Technical Documentation", "Business Proposal", "Legal Document", "Academic Paper", "General Article", "Other"]

# Create the uploads directory if it doesn't exist
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Save the file to the file system
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Extract text content
        try:
            text_content = contents.decode("utf-8")
        except Exception as e: # TODO: maybe do a return instead?
            text_content = "" # Set text_content to an empty string in case of an error
            print(f"Error decoding file {file.filename}: {e}")

        # Classify the document
        classification_result = classify_document(text_content)  # Call classification function

        # Store metadata in the database (including file path)
        doc = Documents(
            filename=file.filename, 
            file_path = file_path, 
            content=text_content, 
            category=classification_result['category'], 
            confidence=str(classification_result['scores'][classification_result['category']]), 
            upload_time=datetime.datetime.now()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return {
            "filename": doc.filename, 
            "category": classification_result['category'], 
            "scores": classification_result['scores']
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/get_documents")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Documents).all()
    return [{"id": doc.id, "filename": doc.filename, "category": doc.category, "confidence": doc.confidence, "upload_time": doc.upload_time.isoformat()} for doc in documents]

import numpy as np
from transformers import pipeline

from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")
candidate_labels = ["Technical Documentation", "Business Proposal", "Legal Document", "Academic Paper", "General Article", "Other"]

def classify_document(text, chunk_size=750):
    if len(text.strip()) <= chunk_size:
        result = classifier(text, candidate_labels, multi_label=False)
        return {
            'category': result['labels'][0],
            'scores': dict(zip(result['labels'], result['scores']))
        }

    overlap = 150  # Number of overlapping characters
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]
    chunk_results = []

    for i, chunk in enumerate(chunks):
        print(f"Classifying chunk {i+1} of {len(chunks)}...")
        try:
            result = classifier(chunk, candidate_labels, multi_label=False)
            chunk_results.append({
                'category': result['labels'][0],
                'scores': dict(zip(result['labels'], result['scores'])),
                'length': len(chunk)
            })
        except Exception as e:
            print(f"Error classifying chunk {i+1}: {e}")
            continue

    if not chunk_results:
        return {'category': 'Other', 'scores': {label: 0.0 for label in candidate_labels}}

    # Weighted voting for category selection
    category_counts = {}
    for result in chunk_results:
        category = result['category']
        weight = result['length']
        category_counts[category] = category_counts.get(category, 0) + weight

    predicted_category = max(category_counts, key=category_counts.get)

    # Correctly calculate weighted average scores for the predicted category ONLY
    weighted_scores = {label: 0.0 for label in candidate_labels}
    total_weighted_length_for_category = sum(
        result['length'] for result in chunk_results if result['category'] == predicted_category
    )

    if total_weighted_length_for_category == 0: # Handle edge case where no chunks match the selected category
        return {'category': 'Other', 'scores': {label: 0.0 for label in candidate_labels}}

    for result in chunk_results:
        if result['category'] == predicted_category:
            weight = result['length'] / total_weighted_length_for_category
            for label, score in result['scores'].items():
                weighted_scores[label] += score * weight

    return {'category': predicted_category, 'scores': weighted_scores}