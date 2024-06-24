from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from typing import List
from icecream import ic
from aiogram.types import KeyboardButton as KButton
from aiogram.types import InlineKeyboardMarkup as InlKB
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton as InKButton
from loader import bot

rm = ReplyKeyboardRemove()


def create_keyboard_select(all_list : List[tuple]) -> InlKB:
  builder = InlineKeyboardBuilder()
  for element in all_list:
    for i in range(1,3):
      builder.button(text=f"{element[i]}", callback_data=f"id {element[0]}" )
  builder.adjust(1)
  return builder.as_markup()

cancel = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KButton(text = "Отмена ❌")]],one_time_keyboard=True)
def create_keyboard_edit(id : str):
  res = InlKB(inline_keyboard=[
    [InKButton(text = "Изменить адрес 🏙", callback_data=f"edit,address,{id}")],
    [InKButton(text="Изменить компанию 📗",callback_data=f"edit,company_name,{id}")],
    [InKButton(text="Изменить комментарий 💬",callback_data=f"edit,Comment,{id}")],
    [InKButton(text = "⬅️ Назад", callback_data="Back")]
  ])
  return res

keyboard_back = InlKB(inline_keyboard=[
  [InKButton(text = "⬅️ Назад", callback_data="Back")]
])

keyboard_YesNo = InlKB(inline_keyboard=[
  [InKButton(text = "Да✅", callback_data="Yes"),InKButton(text="Нет❌",callback_data="No")]
]
)
keyboard_right = InlKB(inline_keyboard=[
  [InKButton(text = "Всё правильно✅", callback_data="Yes"),InKButton(text="Отмена❌",callback_data="No")]
]
)

keyboard_Markup = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KButton(text = "KB1")],
                                                              [KButton(text = "KB2")]])

keyboard_Inline =InlKB(inline_keyboard=[[InKButton(text = "kb",callback_data="kb")]])
