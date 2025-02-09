from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    UPLOAD_DIRECTORY: str = "uploads"
    LOGS_DIRECTORY: str = "logs"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:4200"]
    MODEL_NAME: str = "facebook/bart-large-mnli"
    CHUNK_SIZE: int = 750
    CANDIDATE_LABELS: list[str] = [
        "Technical Documentation",
        "Business Proposal",
        "Legal Document",
        "Academic Paper",
        "General Article",
        "Other"
    ]

settings = Settings()