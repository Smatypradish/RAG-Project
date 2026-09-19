from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Admin credentials. ADMIN_PASSWORD must be set in .env —
    # login fails closed if it is empty.
    admin_username: str = "admin"
    admin_password: str = ""

    # Session tokens are HMAC-signed and expire after this many minutes.
    session_ttl_minutes: int = 60

    # Comma-separated list of allowed CORS origins for the frontend.
    cors_origins: str = "http://localhost:5173"

    chromadb_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k: int = 5

    # Upload constraints.
    max_upload_size_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("chunk_overlap")
    @classmethod
    def overlap_smaller_than_chunk(cls, v, info):
        chunk_size = info.data.get("chunk_size", 800)
        if v >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()

