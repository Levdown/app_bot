from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import token
from keyboards import *
import uuid
import logging
import sqlite3
import datetime

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""create table if not exists admins
(ex_id integer)
""")

cursor.execute("""create table if not exists application
(ex_id integer, name text, phone integer, day text, confirm text, uuid text)
""")

class Form(StatesGroup):
    name = State()  
    phone = State()
    day = State()
    confirm = State()

class RejectUUID():
    def __init__(self, uuid):
        self.uuid = uuid

reject_message = {}

def save_app(ex_id, name, phone, day, uuid):
    cursor.execute('insert into application (ex_id, name, phone, day, confirm, uuid) VALUES (?, ?, ?, ?, ?, ?)', [ex_id, name, phone, day, 'Рассматривается', uuid])
    conn.commit()

def approve_app(uuid):
    cursor.execute('update application set confirm=? where uuid=?', ['Одобрено', uuid])
    conn.commit()

def reject_app(uuid):
    cursor.execute('update application set confirm=? where uuid=?', ['Отклонено', uuid])
    conn.commit()

def get_app(uuid):
    data = cursor.execute('select name, phone, day, confirm from application where uuid=?', [uuid]).fetchone()
    return f'Имя: {data[0]}\nТелефон: {data[1]}\nДата: {data[2]}\nСтатус: {data[3]}'

def get_apps(ex_id):
    data = cursor.execute('select name, phone, day, confirm from application where ex_id=?', [ex_id]).fetchall()
    if data:
        message = ''
        for i in data:
            message += f'Имя: {i[0]}\nТелефон: {i[1]}\nДата: {i[2]}\nСтатус: {i[3]}\n\n'
        return message
    else:
        return 'У вас пока нет заявок'

def get_id(uuid):
    id_ = cursor.execute('select ex_id from application where uuid=?', [uuid]).fetchone()
    print(id_)
    return id_[0]

def check_admin(ex_id):
    ids = cursor.execute('select * from admins').fetchall()
    for i in ids:
        if i[0] == ex_id:
            return True 
    return False

def get_admins():
    ids = cursor.execute('select * from admins').fetchall()
    return ids

def add_admin(ex_id):
    cursor.execute('insert into admins (ex_id) VALUES (?)', [ex_id])
    conn.commit()

def last_app():
    data = cursor.execute('select name, phone, day, confirm from application').fetchall()
    if data:
        message = ''
        for i in data[-10:]:
            message += f'Имя: {i[0]}\nТелефон: {i[1]}\nДата: {i[2]}\nСтатус: {i[3]}\n\n'
        return message
    else:
        return 'Заявок нет'    


@dp.message_handler(commands=['admin'])
async def admin_message(message: types.Message):
    if check_admin(message.chat.id):
        await bot.send_message(message.chat.id, 'Админ панель', reply_markup=admin_markup())
    else:
        await bot.send_message(message.chat.id, 'Вы пока не админ\nЧтобы добавить свой id в список введите команду /adminme')


@dp.message_handler(commands=['adminme'])
async def admin_message(message: types.Message):
    if check_admin(message.chat.id):
        add_admin(message.chat.id)
        await bot.send_message(message.chat.id, 'Вы добавлены в админы')
    else:
        await bot.send_message(message.chat.id, 'Вы уже админ')


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет, с помощью этого бота вы сможете оставить заявку, а админ сможет ее одобрить!', reply_markup=main_markup())
    await bot.send_message(message.chat.id, 'Все доступные команды, доступны по нажатию на кнопку "Команды"', reply_markup=reply_markup())


@dp.message_handler()
async def text_message(message: types.Message):
    if message.text == 'Команды':
        await bot.send_message(message.chat.id, '/admin - админ панель\n\n/adminme - стать админом\n\n/start - начало', reply_markup=reply_markup())
    else:
        uuid_ = reject_message[message.chat.id].uuid
        ex_id = get_id(uuid_)
        reject_app(uuid_)
        app_data = get_app(uuid_)
        await bot.send_message(int(ex_id), f'Ваша заявка отклонена\n\n{app_data}\n\nПричина:\n{message.text}')
        await bot.send_message(message.chat.id, 'Сообщение отправлено\nЗаявка отклонена', reply_markup=main_markup())
        del reject_message[message.chat.id]


@dp.callback_query_handler()
async def main_inline_message(query: types.CallbackQuery):
    data = query.data 
    if data == 'new_app':
        await bot.send_message(query.message.chat.id, 'Началась процедура заполнения заявки\n\nВведите свое имя:', reply_markup=go_main())
        await Form.name.set()

    elif data == 'main_menu':
        await bot.send_message(query.message.chat.id, 'Главное меню', reply_markups = main_markup())

    elif data == 'my_app':
        apps = get_apps(query.message.chat.id)
        await bot.send_message(query.message.chat.id, apps, reply_markup=main_markup())

    elif data == 'last_app':
        await bot.send_message(query.message.chat.id, last_app())

    elif data.startswith('approve_'):
        uuid_ = data.split('_')[1]
        approve_app(uuid_)
        app_data = get_app(uuid_)
        ex_id = get_id(uuid_)
        await bot.send_message(int(ex_id), f'Ваша заявка одобрена\n\n{app_data}', reply_markup=main_markup())
        await bot.send_message(query.message.chat.id, 'Заявка одобрена')

    elif data.startswith('reject_'):
        uuid_ = data.split('_')[1]
        await bot.send_message(query.message.chat.id, 'Напишите причину отказа')
        reject_message[query.message.chat.id] = RejectUUID(uuid_)
        


@dp.callback_query_handler(state=Form.name)
async def name_inline_message(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    if data == 'main_menu':
        await state.finish()
        await bot.send_message(query.message.chat.id, 'Главное меню', reply_markup=main_markup())


@dp.message_handler(state=Form.name)
async def get_name(message, state: FSMContext):
    if all(char.isalpha() or char.isspace() for char in message.text):
        await state.update_data(name=message.text)
        await bot.send_message(message.chat.id, f"Отлично, {message.text}, теперь введите свой номер:", reply_markup=main_back())
        await Form.phone.set()
    else:
        await bot.send_message(message.chat.id, 'Имя введено некорректно, введите имя еще раз', reply_markup=go_main())
    

@dp.callback_query_handler(state=Form.phone)
async def phone_inline_message(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    if data == 'main_menu':
        await state.finish()
        await bot.send_message(query.message.chat.id, 'Главное меню', reply_markup=main_markup())
    elif data == 'back':
        await bot.send_message(query.message.chat.id, 'Введите свое имя:', reply_markup=go_main())
        await Form.name.set()


@dp.message_handler(state=Form.phone)
async def get_phone(message, state: FSMContext):
    if message.text.startswith('+'):
        phone = message.text[1:]
    else:
        phone = message.text

    if phone.isdigit() and len(phone) == 11:
        await bot.send_message(message.chat.id, 'Отлично, теперь введите дату записи в формате ДД.ММ.ГГГГ', reply_markup=main_back())
        await state.update_data(phone=phone)
        await Form.day.set()
    else:
        await bot.send_message(message.chat.id, 'Телефон должен содержать 11 символов и состоять только из цифр\n\nВведите еще раз', reply_markup=main_back())


@dp.callback_query_handler(state=Form.day)
async def day_inline_message(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    if data == 'main_menu':
        await state.finish()
        await bot.send_message(query.message.chat.id, 'Главное меню', reply_markup=main_markup())
    elif data == 'back':
        await bot.send_message(query.message.chat.id, 'Введите свой номер:', reply_markup=go_main())
        await Form.phone.set()


@dp.message_handler(state=Form.day)
async def get_day(message, state: FSMContext):
    try:
        day = str(datetime.datetime.strptime(message.text, "%d.%m.%Y")).split(' ')[0]
        await state.update_data(day=day)
        data = await state.get_data()
        await bot.send_message(message.chat.id, f"Имя: {data['name']}\n\nТелефон: {data['phone']}\n\nДата: {data['day']}", reply_markup=confirm())
        await Form.confirm.set()
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Дата введена не верно, введите дату еще раз в формате ДД.ММ.ГГГГ')


@dp.callback_query_handler(state=Form.confirm)
async def confirm_inline_message(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    if data == 'main_menu':
        await state.finish()
        await bot.send_message(query.message.chat.id, 'Главное меню', reply_markup=main_markup())

    elif data == 'back':
        await bot.send_message(query.message.chat.id, 'Введите дату записи в формате ДД.ММ.ГГГГ:', reply_markup=go_main())
        await Form.day.set()

    elif data == 'send':
        data_state = await state.get_data()
        uuid_ = str(uuid.uuid4())
        admin_ids = get_admins()

        for i in admin_ids:
            try:
                await bot.send_message(int(i[0]), f"Новая заявка:\n\nИмя: {data_state['name']}\nТелефон: {data_state['phone']}\nДата: {data_state['day']}", reply_markup=admin_check(uuid_))
            except:
                pass

        save_app(query.message.chat.id, data_state['name'], data_state['phone'], data_state['day'], uuid_)
        await bot.send_message(query.message.chat.id, 'Ваша заявка успешно отправлена админу', reply_markup=main_markup())
        await state.finish()


executor.start_polling(dp, skip_updates=True)