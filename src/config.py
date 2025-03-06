from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NYT_API_KEY: str
    MCP_PORT: int = 8000
    MCP_HOST: str = "0.0.0.0"

    class Config:
        env_file = ".env"

settings = Settings() 