from typing import List
from sqlalchemy.orm import Session
from database_model import Documents
from datetime import datetime

class DocumentHandler:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, filename: str, file_path: str, 
                       content: str, category: str, confidence: str) -> Documents:
        doc = Documents(
            filename=filename,
            file_path=file_path,
            content=content,
            category=category,
            confidence=confidence,
            upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_all_documents(self) -> List[Documents]:
        return self.db.query(Documents).all()