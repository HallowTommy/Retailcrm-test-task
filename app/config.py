from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    retailcrm_api_key: str
    retailcrm_api_url: str
    app_port: int = 8000

    class Config:
        env_file = ".env.example"


settings = Settings()
