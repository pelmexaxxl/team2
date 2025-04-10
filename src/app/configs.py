import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    POSTRGES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    POSTRGES_DB = os.getenv('POSTGRES_DB')
    
    @property
    def get_db_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTRGES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTRGES_DB}'


settings = Config()
