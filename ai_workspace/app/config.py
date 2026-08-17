from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment variables and the .env file.

    Every field can be overridden without touching code — e.g. put
    OLLAMA_BASE_URL=http://192.168.1.50:11434 in .env to use a remote Ollama.
    """

    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "mistral"

    # connect = seconds to establish the connection to Ollama.
    # read = seconds to wait for the next piece of a reply. Local generation
    # is slow (model load + token generation), so read is generous.
    connect_timeout: float = 5.0
    read_timeout: float = 120.0

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Read settings once and reuse them (lru_cache makes this a singleton)."""
    return Settings()
