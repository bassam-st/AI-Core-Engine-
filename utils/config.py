from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Al-Core-Engine"
    database_url: str = "bassam.db"
    knowledge_path: str = "knowledge/elite_knowledge.json"
    max_memory_facts: int = 10000
    learning_interval_hours: int = 6
    search_timeout: int = 12
    max_web_results: int = 6
    
    class Config:
        env_file = ".env"

settings = Settings()
