from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.database.request import Request
from utils.checker import Checker
from utils.excel import Excel_db

excl = Excel_db()
rq = Request()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
chk = Checker(bot)