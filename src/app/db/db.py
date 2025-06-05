from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.configs import settings


engine = create_async_engine(url=settings.get_db_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
