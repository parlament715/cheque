from aiogram import BaseMiddleware
from aiogram import types
from typing import Callable, Dict, Any, Awaitable,Union
from config import  today
from loader import bot,rq
from icecream import ic
from aiogram.utils.deep_linking import decode_payload



class CheckerSubscriptionsOnChannel(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any]
                                        ) -> Any:
            return await handler(event,data)


class CheckerOnCallbackData(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any]
                                        ) -> Any:
            return await handler(event,data)
