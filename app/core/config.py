from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings manager for loading environment variables and defaults.
    
    Args:
        DATABASE_URL (str): Database connection URL.
        ROUTE_CHECK_INTERVAL (int): Interval (in seconds) for route checking.
        APITOKEN (str): Secret API token for authentication.
    """
    DATABASE_URL: str = Field("sqlite:///./routes.db", env="DATABASE_URL")
    ROUTE_CHECK_INTERVAL: int = Field(10, env="ROUTE_CHECK_INTERVAL")
    APITOKEN: str = Field("this_is_something_secret", env="APITOKEN")

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }

settings = Settings()
