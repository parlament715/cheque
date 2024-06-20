import logging
import asyncio
from app.handlers import router
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from loader import bot, dp, rq
from app.middelwares import CheckerSubscriptionsOnChannel,CheckerOnCallbackData



async def main():
    dp.message.outer_middleware.register(CheckerSubscriptionsOnChannel())
    dp.callback_query.outer_middleware.register(CheckerOnCallbackData())
    
    
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s :%(name)s -%(asctime)s'
                        ,level=logging.DEBUG)
    asyncio.run(main())


