from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.database.request import Request
from utils.checker import Checker

rq = Request("request.db")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
chk = Checker(bot)