from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram import F,Router
from aiogram.fsm.context import FSMContext
from loader import bot, rq , chk
from config import today
from icecream import ic
from app.keyboard import keyboard_Inline, keyboard_Markup
from random import randint

router = Router()

@router.message(CommandStart())
async def start_reaction(message: Message, state : FSMContext):
    await message.answer("Отправьте чек в формате html")
    await state.set_state("waiting cheque.html")

# @router.message(StateFilter("waiting cheque.html"))
@router.message()
async def response_cheque(message : Message,state : FSMContext):
    try :
        file_id = message.document.file_id
        file_name = message.document.file_name
    except:
        await message.answer("Файл не загружен, попробуйте ещё")
        ### не меняем сиейт
        return
    response = await chk.check_all(file_id = message.document.file_id,file_name = message.document.file_name)
    if response in ["Нет файла","Расширение не .html","Это не кассовый чек"]:
        await message.answer(response + ", попробуйте ещё раз")
        #### не меняем стейт
        return
    elif response == "Здесь нет адреса":
        await message.answer("Напишите пожалуйста адрес")
        ### передать стейт
    elif response == "Не удалось найти улицу в адресе":
        await message.answer('Не удалось найти найти улицу в адресе, напишите её вручную')
        ### передать стейт
    else:
        await message.answer(f"Улица : {response}")
    
    
    



#     a = randint(1,2)
#     if a == 1:
#         await message.answer("Сообщение",reply_markup=keyboard_Inline)
#     elif a == 2:
#         await message.answer("Сообщение",reply_markup=keyboard_Markup)

# @router.message(lambda _ : (F.data == "KB1") or (F.data == "KB2"))
# async def kb_reaction(message : Message):
#     await message.answer("Ты молодец!")


# @router.callback_query(F.data == "kb")
# async def kbb_reaction(call : CallbackQuery ):
#     await call.answer()
#     await call.message.answer("Ты холодец!")