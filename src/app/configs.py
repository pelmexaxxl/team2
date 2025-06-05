import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    yandex_api_key: str
    ADMIN_USER_ID: int

    class Config:
        env_file = ".env"
    
    @property
    def get_db_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'
    
    @property
    def database_url(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'


settings = Settings()

