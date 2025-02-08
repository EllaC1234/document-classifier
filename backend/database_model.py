# SQLite is a file-based database model that doesn't require a database server. 

from sqlalchemy import create_engine, Column, Integer, String, DateTime
# ORM is an object-relational mapping library that allows you to use Python objects to interact with a database rather than SQL queries.
from sqlalchemy.orm import sessionmaker, declarative_base 

DATABASE_URL = "sqlite:///./documents.db" # SQLite database file named documents.db in the current directory

engine = create_engine(DATABASE_URL) # Manages database connection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Session for database interaction
Base = declarative_base() # Defines database models

# Represents a table in the database
class Documents(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    content = Column(String)
    category = Column(String)
    confidence = Column(String)
    upload_time = Column(DateTime)

Base.metadata.create_all(bind=engine) # Create the table

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()