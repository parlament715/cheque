from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter,Command
from aiogram import F,Router
from aiogram.fsm.context import FSMContext
from loader import bot, rq , chk
from config import today
from icecream import ic
from app.keyboard import (keyboard_Inline, keyboard_Markup, keyboard_YesNo, keyboard_right,
create_keyboard_select, keyboard_back, create_keyboard_edit, cancel, names_company,)
from random import randint
from aiogram.enums.parse_mode import ParseMode
from utils import card_template
router = Router()

@router.message(CommandStart())
async def start_reaction(message: Message, state : FSMContext):
    await message.answer("Привет! Меня зовут drnkt-bot. Я здесь, чтобы ты присылал мне чеки из приложения «Проверка чеков ФНС»: После сканирования, жми «Действия с чеком - поделиться - формат html - отправить через telegram - drnkt_bot. Не забудь проверить, верный ли адрес торговой точки в чеке!")

@router.message(F.content_type.in_(["document"]))
# @router.message()
async def add_cheque(message : Message,state : FSMContext):
    try :
        file_id = message.document.file_id
        file_name = message.document.file_name
    except:
        await message.answer("Файл не загружен, попробуйте ещё")
        ### не меняем сиейт
        return
    
    try:
        response = await chk.check_all(file_id = message.document.file_id,file_name = message.document.file_name)
    except Exception as err:
        err = err.args[0]        
        if err in ["Нет файла","Расширение не .html","Это не кассовый чек"]:
            await message.answer(err + ", попробуйте ещё раз")
            #### не меняем стейт
            return
    await state.set_data(response)
    await state.update_data(user_name_telegram = message.from_user.username)
    if not response["address"]:
        await message.answer("Программе не удалось найти адрес, напишите его вручную")
        await state.set_state("update address")
        return
    await message.answer("Напишите название компании",reply_markup=names_company)
    await state.set_state("take company name")


@router.message(StateFilter("update address"))
async def update_address(message : Message, state : FSMContext):
    # ic(message.text)
    await state.update_data(address = message.text)
    await message.answer("Напишите название компании",reply_markup=names_company)
    await state.set_state("take company name")

    
@router.message(StateFilter("take company name"))
async def take_company_name(message : Message, state : FSMContext):
    await state.update_data(company_name = message.text)
    await state.set_state("comment")
    await message.answer("Хотите добавить комментарий?",reply_markup=keyboard_YesNo)

@router.callback_query(F.data == "Yes",StateFilter("comment"))
async def callback_Yes(call : CallbackQuery,state : FSMContext):
    await bot.edit_message_text("Напишите комментарий",call.from_user.id,call.message.message_id)
    await state.set_state("add comment")

@router.message(StateFilter("add comment"))
async def add_commentRight(message : Message, state : FSMContext):
    await state.update_data(Comment = message.text)
    data = await state.get_data()
    await message.answer(card_template.format_text(card_template.text_template,data),
    parse_mode=ParseMode.HTML,
    reply_markup=keyboard_right)
    await state.set_state("right")

@router.callback_query(F.data == "No",StateFilter("comment"))
async def callback_No(call : CallbackQuery, state : FSMContext):
    await state.update_data(Comment = "---")
    data = await state.get_data()
    await bot.edit_message_text(card_template.format_text(card_template.text_template,data),
    call.from_user.id,call.message.message_id,reply_markup=keyboard_right,parse_mode=ParseMode.HTML)
    await state.set_state("right")

@router.callback_query(F.data == "Yes",StateFilter("right"))
async def callback_Yes_right(call : CallbackQuery,state : FSMContext):
    data = await state.get_data()
    ### Загрузить в бд
    with rq:
        rq.write_insert("cards",[
            ("id_telegram",call.from_user.id),
            ("user_name_telegram",call.from_user.username),
            ("company_name",data["company_name"]),
            ("date_time",data["date_time"]),
            ("address",data["address"]),
            ("cheque_number",data["cheque_number"]),
            ("FD",data["FD"]),
            ("shift_number",data["shift_number"]),
            ("Comment",data["Comment"])
            ])
    ###
    await bot.edit_message_text("Карточка загружена в базу данных",call.from_user.id,call.message.message_id)
    await state.clear()

@router.callback_query(F.data == "No",StateFilter("right"))
async def callback_No(call : CallbackQuery, state : FSMContext):
    await state.clear()
    await bot.edit_message_text("Отправьте чек в формате html",call.from_user.id,call.message.message_id)
    await state.set_state("waiting cheque.html")

@router.message(Command("search"))
async def search(message : Message, state : FSMContext):
    await state.clear()
    await message.answer("Напишите пожалуйста улицу, по которой вы хотите совершить поиск")
    await state.set_state("await search")

@router.message(StateFilter("await search"))
async def await_search(message : Message, state : FSMContext):
    if len(message.text) < 3:
        await message.answer("Строка поиска должна быть не менее 3-ёх символов")
        return
    await state.update_data(filter = message.text, type = "text")
    with rq:
        res =rq.select_many("cards",["id", "company_name", "address"],f'address LIKE "%{message.text}%"')
    if not res:
        await message.answer("По этому запросу ничего не найдено, попробуйте ещё раз")
        return
    await message.answer("Выберете место",reply_markup=create_keyboard_select(res))
    await state.set_state("id")
    
@router.callback_query(F.data.startswith("id"),StateFilter("id"))
async def get_card(call : CallbackQuery, state : FSMContext):
    state_data = await state.get_data()
    with rq:
        res = rq.select_one("cards",["@*"],f'"id"={call.data.split()[-1]}')
    columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","Comment")
    data = dict(zip(columns,res))
    text_message = card_template.format_text(card_template.text,data)
    if state_data["type"] == "id":
        await bot.edit_message_text(text_message,call.from_user.id,call.message.message_id,reply_markup=create_keyboard_edit(call.data.split()[-1]),parse_mode=ParseMode.HTML)
    elif state_data["type"] == "text":
        await bot.edit_message_text(text_message,call.from_user.id,call.message.message_id,reply_markup=keyboard_back,parse_mode=ParseMode.HTML)
    await state.set_state("button")

@router.callback_query(StateFilter("button"),F.data.startswith("edit"))
async def button(call : CallbackQuery, state : FSMContext):
    await state.update_data(edit = call.data.split(",")[1],id =call.data.split(",")[2] )
    if "address" in call.data:
        await call.message.answer("Введите новый адрес",reply_markup=cancel)
    elif "company_name" in call.data:
        await call.message.answer("Введите новое название компании",reply_markup=cancel)
    elif "Comment" in call.data:
        await call.message.answer("Введите новый комментарий",reply_markup=cancel)
    await state.set_state("edit await")
    await call.answer()


@router.message(StateFilter("edit await"))
async def edit_await(message : Message,state : FSMContext):
    state_data = await state.get_data()
    with rq:
        if message.text != "Отмена ❌":
            rq.write_update("cards",[(state_data["edit"],message.text)],f'id = {state_data["id"]}')
        res = rq.select_one("cards", ["@*"], f'id = {state_data["id"]}')
    columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","Comment")
    data = dict(zip(columns,res))
    await message.answer(card_template.format_text(card_template.text,data),
    reply_markup=create_keyboard_edit(state_data["id"]),parse_mode=ParseMode.HTML)
    await state.set_state("button")

@router.callback_query(StateFilter("button"),F.data == "Back")
async def back(call :CallbackQuery,state: FSMContext):
    data = await state.get_data()
    if data["type"] == "id":
        with rq:
            res =rq.select_many("cards",["id", "company_name", "address"],f'id_telegram = {data["filter"]}')
    elif data["type"] == "text":
        with rq:
            res =rq.select_many("cards",["id", "company_name", "address"],f'address LIKE "%{data["filter"]}%"')
    await bot.edit_message_text("Выберете место",call.from_user.id,call.message.message_id,reply_markup=create_keyboard_select(res))
    await state.set_state("id")

@router.message(Command("edit"))
async def list_my_cards(message : Message, state : FSMContext):
    await state.clear()
    await state.update_data(type = "id",filter = message.from_user.id)
    with rq:
        res =rq.select_many("cards",["id", "company_name", "address"],f'id_telegram = {message.from_user.id}')
    if not res:
        await message.answer("У вас пока ещё нет записей")
        return
    await message.answer("Выберете место",reply_markup=create_keyboard_select(res))
    await state.set_state("id")


