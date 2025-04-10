from typing import Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.db.db import get_async_session


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__() 

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[None]], 
        event: Message,
        data: dict
        ) -> None:
        async for session in get_async_session():
            data['session'] = session
            return await handler(event, data)
