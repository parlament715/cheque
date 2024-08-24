from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, StateFilter,Command
from aiogram import F,Router
from aiogram.fsm.context import FSMContext
from loader import bot, rq , chk
from config import today, ADMIN
from utils.excel import Excel_db, Excel_read
from icecream import ic
from app.keyboard import (keyboard_Inline, keyboard_Markup, keyboard_YesNo, keyboard_right,
create_keyboard_select, keyboard_back, create_keyboard_edit, cancel, names_company, keyboard_try_again, keyboard_load)
from random import randint
from aiogram.enums.parse_mode import ParseMode
from utils import card_template
from utils.parser import Parse
import logging
router = Router()

logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"log/{__name__}.log", mode='w', encoding = "UTF-8")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)



@router.message(CommandStart())
async def start_reaction(message: Message, state : FSMContext):
    logger.info(f"{message.from_user.username} нажал кнопку старт")
    await message.answer("Привет! Меня зовут drnkt-bot. Я здесь, чтобы ты присылал мне чеки из приложения «Проверка чеков ФНС»: После сканирования, жми «Действия с чеком - поделиться - формат html - отправить через telegram - drnkt_bot. Не забудь проверить, верный ли адрес торговой точки в чеке!")

@router.message(F.content_type.in_(["document"]),StateFilter("load await"))
async def await_load(message : Message, state : FSMContext):
    await bot.send_chat_action(message.from_user.id, action="find_location")
    try :
        file_id = message.document.file_id
        file_name = message.document.file_name
    except:
        logger.error(f"Не удалось загрузить {message.from_user.username}")
        await message.answer("Файл не загружен, попробуйте ещё")
        ### не меняем сиейт
        return
    if file_name:
        if file_name.split(".")[-1] == "xlsx":
            file_name = "load.xlsx"
            file = await bot.get_file(file_id)
            # Укажите папку дл
            await bot.download_file(file.file_path,file_name)
            logger.info(f"{message.from_user.username} загрузил таблицу excel")
            await Excel_read.read(file_name)
            logger.info(f"{message.from_user.username} excel таблица прочитана")
            await message.answer("Таблица загружена ✅")
            await state.clear()
    else:
        await message.answer("Файл не загружен, попробуйте ещё")
        logger.error(f"Не удалось загрузить {message.from_user.username}")

@router.message(F.content_type.in_(["document"]))
# @router.message()
async def add_cheque(message : Message,state : FSMContext):
    logger.info(f"{message.from_user.username} отправлен чек")
    await bot.send_chat_action(message.from_user.id, action="find_location")
    try :
        file_id = message.document.file_id
        file_name = message.document.file_name
    except:
        logger.error(f"Не удалось загрузить {message.from_user.username}")
        await message.answer("Файл не загружен, попробуйте ещё")
        ### не меняем сиейт
        return
    
    try:
        response = await chk.check_all(file_id = message.document.file_id,file_name = message.document.file_name)
    except Exception as err:
        logger.error(f"Error in {message.from_user.username}: {err}")
        err = err.args[0]        
        if err in ["Нет файла","Расширение не .html","Это не кассовый чек"]:
            logger.info(f"{message.from_user.username} пробует ещё раз")
            await message.answer(err + ", попробуйте ещё раз")
            #### не меняем стейт
            return
    await state.set_data(response)
    await state.update_data(user_name_telegram = message.from_user.username)
    if not response["address"]:### доделать
        logger.warning(f"{message.from_user.username} не удалось найти адрес")
        await state.update_data(type_update = "add address")
        await message.answer("Программе не удалось найти адрес, напишите его вручную\nВАЖНО указать в адресе город, улицу и номер дома!!!")
        await state.set_state("update address")
        return
    if response["coordinates"] is None:
        logger.warning(f"{message.from_user.username} оставляем адрес как есть, статус 2")
        await state.update_data(coordinates = "---")
        await state.update_data(status = 2)
        ic("status 2")
    else:
        logger.info(f"{message.from_user.username} нашли координаты, адрес правильный, статус 1")
        ic("status 1")
        await state.update_data(status = 1)
    
    await message.answer("Напишите название компании",reply_markup=names_company)
    await state.set_state("take company name")


@router.message(StateFilter("update address"))
async def update_address(message : Message, state : FSMContext):
    logger.info(f"{message.from_user.username} корректирует адрес")
    await bot.send_chat_action(message.from_user.id, action="find_location")
    coordinates, right_address = await Parse.parse_coordinates_and_address(message.text)
    await state.update_data(incorrect_address = message.text,right_coordinates = coordinates,right_address = right_address)
    if coordinates is None:
        logger.warning(f"{message.from_user.username} не удалось распознать адрес, статус 2")
        await message.answer("Программа не смогла распознать адрес",reply_markup=keyboard_try_again)
        await state.set_state("try_again_address")
        return
    else:
        logger.info(f"{message.from_user.username} координаты распознаны, спрашиваем оставить ли")
        await message.answer(f"Программе удалось распознать ваш адрес?\n{right_address}",reply_markup=keyboard_YesNo)
        await state.set_state("agree")
    
    
@router.callback_query(StateFilter("agree"))
async def check_agree(call : CallbackQuery, state : FSMContext):
    if call.data == "Yes":
        logger.info(f"{call.from_user.username} оставляем правильные координаты, статус 1")
        data = await state.get_data()
        if data["type_update"] == "add address":
            await state.update_data(address = data["right_address"],coordinates = data["right_coordinates"],status = 1)
            await call.message.delete()
            await call.message.answer('Напишите название компании',reply_markup=names_company)
            await state.set_state("take company name")
        elif data["type_update"] == "update address":
            with rq:
                rq.write_update("cards",[("address",data["right_address"])],f'id={data["id"]}')
                rq.write_update("cards",[("coordinates",data["right_coordinates"])],f'id={data["id"]}')
                rq.write_update("cards",[("status",1)],f'id={data["id"]}')
                res = rq.select_one("cards", ["@*"], f'id={data["id"]}')
            columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","coordinates","status","comment")
            data = dict(zip(columns,res))
            await call.message.bot.edit_message_text(card_template.format_text(card_template.text,data),call.from_user.id,call.message.message_id,
            reply_markup=create_keyboard_edit(data["id"]),parse_mode=ParseMode.HTML)
            await state.set_state("button")
                

    if call.data == "No":
        logger.info(f"{call.from_user.username} пробуем ещё раз или оставляем неправильный адрес")
        await call.message.bot.edit_message_text("Выберете один из вариантов",call.from_user.id,call.message.message_id,reply_markup=keyboard_try_again)
        await state.set_state("try_again_address")
        

    

@router.callback_query(StateFilter("try_again_address"))
async def try_again_address(call : CallbackQuery, state : FSMContext):
    if call.data == "Yes":
        logger.info(f"{call.from_user.username} пробуем ещё раз")
        await call.message.bot.edit_message_text('Попробуйте ещё, для более точного распознавания стоит добавить запятые между частями адреса и такие сокращения как "г.", "ул." и так далее.',call.from_user.id,call.message.message_id)
        await state.set_state("update address")
    elif call.data == "No":
        logger.info(f"{call.from_user.username} оставляем так, статус 2")
        data = await state.get_data()
        if data["type_update"] == "add address":
            await state.update_data(address = data["incorrect_address"],coordinates = "---",status = 2)
            await call.message.delete()
            logger.info(f"{call.from_user.username} спрашиваем название компании")
            await call.message.answer('Напишите название компании',reply_markup=names_company)
            await state.set_state("take company name")
        elif data["type_update"] == "update address":
            with rq:
                rq.write_update("cards",[("address",data["incorrect_address"])],f'id={data["id"]}')
                rq.write_update("cards",[("coordinates","---")],f'id={data["id"]}')
                rq.write_update("cards",[("status",2)],f'id={data["id"]}')
                res = rq.select_one("cards", ["@*"], f'id={data["id"]}')
            columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","coordinates","status","comment")
            data = dict(zip(columns,res))
            await call.message.bot.edit_message_text(card_template.format_text(card_template.text,data),call.from_user.id,call.message.message_id,
            reply_markup=create_keyboard_edit(data["id"]),parse_mode=ParseMode.HTML)
            await state.set_state("button")

@router.message(StateFilter("take company name"))
async def take_company_name(message : Message, state : FSMContext):
    logger.info(f"{message.from_user.username} нужен ли комментарий?")
    await state.update_data(company_name = message.text)
    await state.set_state("comment")
    await message.answer("Хотите добавить комментарий?",reply_markup=keyboard_YesNo)

@router.callback_query(F.data == "Yes",StateFilter("comment"))
async def callback_Yes(call : CallbackQuery,state : FSMContext):
    logger.info(f"{call.from_user.username} да, нужен, спрашиваем комментатрий")
    await bot.edit_message_text("Напишите комментарий",call.from_user.id,call.message.message_id)
    await state.set_state("add comment")

@router.message(StateFilter("add comment"))
async def add_commentRight(message : Message, state : FSMContext):
    logger.info(f"{message.from_user.username} спрашиваем все ли корректно?")
    await state.update_data(comment = message.text)
    data = await state.get_data()
    await message.answer(card_template.format_text(card_template.text_template,data),
    parse_mode=ParseMode.HTML,
    reply_markup=keyboard_right)
    await state.set_state("right")

@router.callback_query(F.data == "No",StateFilter("comment"))
async def callback_No(call : CallbackQuery, state : FSMContext):
    logger.info(f"{call.from_user.username} нет, не нужен, спрашиваем все ли корректно?")
    await state.update_data(comment = "---")
    data = await state.get_data()
    await bot.edit_message_text(card_template.format_text(card_template.text_template,data),
    call.from_user.id,call.message.message_id,reply_markup=keyboard_right,parse_mode=ParseMode.HTML)
    await state.set_state("right")

@router.callback_query(F.data == "Yes",StateFilter("right"))
async def callback_Yes_right(call : CallbackQuery,state : FSMContext):
    data = await state.get_data()
    logger.info(f"{call.from_user.username} да, все верно, загружаем в базу данных")
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
            ("coordinates",data["coordinates"]),
            ("status",data["status"]),
            ("comment",data["comment"])
            ])
    ###
    await bot.edit_message_text("Карточка загружена в базу данных",call.from_user.id,call.message.message_id)
    await state.clear()

@router.callback_query(F.data == "No",StateFilter("right"))
async def callback_No(call : CallbackQuery, state : FSMContext):
    logger.info(f"{call.from_user.username} нет, ожидаем снова файл")
    await state.clear()
    await bot.edit_message_text("Отправьте чек в формате html",call.from_user.id,call.message.message_id)
    await state.set_state("waiting cheque.html")

@router.message(Command("search"))
async def search(message : Message, state : FSMContext):
    logger.info(f"{message.from_user.username} воспользовался командой поиска")
    await state.clear()
    await message.answer("Напишите пожалуйста улицу, по которой вы хотите совершить поиск",reply_markup=cancel)
    await state.set_state("await search")

@router.message(StateFilter("await search"))
async def await_search(message : Message, state : FSMContext):
    if message.text == "Отмена ❌":
        logger.info(f"{message.from_user.username} отменил поиск")
        await state.clear()
        return
    if len(message.text) < 3:
        logger.info(f"{message.from_user.username} сильно короткий запрос")
        await message.answer("Строка поиска должна быть не менее 3-ёх символов")
        return
    await state.update_data(filter = message.text, type = "text")
    with rq:
        res =rq.select_many("cards",["id", "company_name", "address"],f'address LIKE "%{message.text}%"')
    if not res:
        await message.answer("По этому запросу ничего не найдено, попробуйте ещё раз")
        return
    logger.info(f"{message.from_user.username} нашёл {len(res)} карточек по запросу {message.text}")
    await message.answer("Выберете место",reply_markup=create_keyboard_select(res))
    await state.set_state("id")
    
@router.callback_query(F.data.startswith("id"),StateFilter("id"))
async def get_card(call : CallbackQuery, state : FSMContext):
    state_data = await state.get_data()
    logger.info(f"{call.from_user.username} берёт карточку с id: {call.data.split()[-1]}")
    with rq:
        res = rq.select_one("cards",["@*"],f'"id"={call.data.split()[-1]}')
    columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","coordinates","status","comment")
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
        logger.info(f"{call.from_user.username} хочет отредактировать адрес")
        await call.message.answer("Введите новый адрес",reply_markup=cancel)
        await state.update_data(type_update = "update address")
        await state.set_state("update address")
    elif "company_name" in call.data:
        logger.info(f"{call.from_user.username} хочет отредактировать название компании")
        await call.message.answer("Введите новое название компании",reply_markup=cancel)
        await state.set_state("edit await")
    elif "comment" in call.data:
        logger.info(f"{call.from_user.username} хочет отредактировать комментарий")
        await call.message.answer("Введите новый комментарий",reply_markup=cancel)
        await state.set_state("edit await")
    await call.answer()


@router.message(StateFilter("edit await"))
async def edit_await(message : Message,state : FSMContext):
    state_data = await state.get_data()
    logger.info(f"{message.from_user.username} отредактировал {state_data["edit"]} на {message.text} у карточки с id:{state_data["id"]}")
    with rq:
        if message.text != "Отмена ❌":
            rq.write_update("cards",[(state_data["edit"],message.text)],f'id = {state_data["id"]}')
        res = rq.select_one("cards", ["@*"], f'id = {state_data["id"]}')
    columns = ("id","id_telegram","user_name_telegram","company_name","date_time","address","cheque_number","FD","shift_number","coordinates","status","comment")
    data = dict(zip(columns,res))
    await message.answer(card_template.format_text(card_template.text,data),
    reply_markup=create_keyboard_edit(state_data["id"]),parse_mode=ParseMode.HTML)
    await state.set_state("button")

@router.callback_query(StateFilter("button"),F.data == "Back")
async def back(call :CallbackQuery,state: FSMContext):
    logger.info(f"{call.from_user.username} нажал кнопку назад")
    data = await state.get_data()
    if data["type"] == "id":
        with rq:
            res =rq.select_many("cards",["id", "company_name", "address"],f'id_telegram = {call.from_user.id}')
    elif data["type"] == "text":
        with rq:
            res =rq.select_many("cards",["id", "company_name", "address"],f'address LIKE "%{data["filter"]}%"')
    await bot.edit_message_text("Выберете место",call.from_user.id,call.message.message_id,reply_markup=create_keyboard_select(res))
    await state.set_state("id")

@router.message(Command("edit"))
async def list_my_cards(message : Message, state : FSMContext):
    logger.info(f"{message.from_user.username} хочет редактировать карточки")
    await state.clear()
    await state.update_data(type = "id",filter = message.from_user.id)
    with rq:
        res =rq.select_many("cards",["id", "company_name", "address"],f'id_telegram = {message.from_user.id}')
    if not res:
        logger.info(f"У {message.from_user.username} нет записей")
        await message.answer("У вас пока ещё нет записей")
        return
    logger.info(f"У {message.from_user.username} {len(res)} записей")
    await message.answer("Выберете место",reply_markup=create_keyboard_select(res))
    await state.set_state("id")


@router.message(Command("admin"))
async def send_excel_tb(message : Message, state : FSMContext):
    if str(message.from_user.id) in ADMIN:
        logger.info(f"{message.from_user.username} спрашиваем скачать или загрузить таблицу")
        await message.answer("Выберете действие",reply_markup=keyboard_load)
        await state.set_state("load")

@router.callback_query(StateFilter("load"))
async def load(call : CallbackQuery, state : FSMContext):
    message = call.message
    ic(call.data)
    if call.data == "Download":
        logger.info(f"{message.from_user.username} хочет получить таблицу excel")
        with rq:
            try:
                Excel_db.create_xl(rq.conn)
            except Exception as ex:
                ic(ex)
                await message.answer("Ошибка, попробуйте ещё раз")
                return
        file = FSInputFile(Excel_db.file_name)
        await bot.send_document(chat_id=message.chat.id,document=file)
        logger.info(f"{message.from_user.username} получил таблицу excel")
        await call.answer()
        await state.clear()
        return
    elif call.data == "Load":
        logger.info(f"{message.from_user.username} хочет загрузить таблицу")
        await message.answer("Отправьте таблицу excel")
        await state.set_state("load await")
        await call.answer()
    
