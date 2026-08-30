from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "SENTINEL-RAG"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/sentinel_rag"
    redis_url: str = "redis://localhost:6380/0"

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
