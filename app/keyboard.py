from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import KeyboardButton as KButton
from aiogram.types import InlineKeyboardMarkup as InlKB
from aiogram.types import InlineKeyboardButton as InKButton
from loader import bot

rm = ReplyKeyboardRemove()

keyboard_Markup = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KButton(text = "KB1")],
                                                              [KButton(text = "KB2")]])

keyboard_Inline =InlKB(inline_keyboard=[[InKButton(text = "kb",callback_data="kb")]])
