from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings manager for loading environment variables and defaults.
    
    Args:
        database_url (str): Database connection URL.
        apitoken (str): Secret API token for authentication.
        port (int): Port for the application to run.
    """
    database_url: str = Field("sqlite:///./routes.db", env="DATABASE_URL")
    apitoken: str = Field("this_is_something_secret", env="APITOKEN")
    port: int = Field(8172, env="PORT")

    # model_config = SettingsConfigDict(env_file='../../../.env', env_file_encoding='utf-8')
    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }

settings = Settings()
