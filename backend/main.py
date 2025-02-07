from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import database_model
from transformers import pipeline
import datetime, os
import numpy as np

app = FastAPI()

# ML Model Loading (Hugging Face)
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")
candidate_labels = ["Technical Documentation", "Business Proposal", "Legal Document", "Academic Paper", "General Article", "Other"]

# Create the uploads directory if it doesn't exist
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(database_model.get_db)):
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
        predicted_category = classify_document(text_content)  # Call classification function

        # Store metadata in the database (including file path)
        doc = database_model.Documents(filename=file.filename, file_path = file_path, content=text_content, category=predicted_category, confidence="N/A", upload_time=datetime.datetime.now())
        db.add(doc)
        db.commit()
        db.refresh(doc)
        # TODO: return the correct information
        return {"id": doc.id, "filename": doc.filename, "category": doc.category, "upload_time": doc.upload_time.isoformat(), "file_path": doc.file_path} # Return file_path

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/get_documents")
def get_documents(db: Session = Depends(database_model.get_db)):
    documents = db.query(database_model.Documents).all()
    return [{"id": doc.id, "filename": doc.filename, "category": doc.category, "confidence": doc.confidence, "upload_time": doc.upload_time.isoformat()} for doc in documents]

def classify_document(text, chunk_size=500):
    # If chunks are not needed, return label
    text_length = len(text)
    if text_length <= chunk_size:
      result = classifier(text, candidate_labels)
      return result['labels'][0]

    # Splits text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, text_length, chunk_size)]
    chunk_probabilities = []

    # For each chunk, classify and store the probabilities
    for i, chunk in enumerate(chunks):
        print(f"Classifying chunk {i+1} of {len(chunks)}...")
        try:
            result = classifier(chunk, candidate_labels)
            chunk_probabilities.append(result['scores']) 
        except Exception as e:
            print(f"Error classifying chunk {i+1}: {e}")
            return "Error"

    # Average probabilities across chunks
    if chunk_probabilities:
        averaged_probabilities = np.mean(chunk_probabilities, axis=0) # Average across categories
        predicted_category_index = np.argmax(averaged_probabilities) # Get index of max probability
        final_category = candidate_labels[predicted_category_index]
    else:
        final_category = "Unknown"

    return final_category