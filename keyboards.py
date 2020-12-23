from aiogram import types

def main_markup():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Оставить заявку', callback_data='new_app')
    btn2 = types.InlineKeyboardButton(text='Ваши заявки', callback_data='my_app')
    return markup.add(btn1).add(btn2)

def go_main():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
    return markup.add(btn1)    

def main_back():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Назад', callback_data='back')
    btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
    return markup.add(btn1).add(btn2)        

def confirm():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Отправить заявку', callback_data='send')
    btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
    btn3= types.InlineKeyboardButton(text='Назад', callback_data='back')
    return markup.add(btn1).add(btn2).add(btn3)

def admin_check(ex_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Одобрить', callback_data=f'approve_{ex_id}')
    btn2 = types.InlineKeyboardButton(text='Отклонить', callback_data=f'reject_{ex_id}')
    return markup.add(btn1).add(btn2)   

def admin_markup():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Последние 10 заявок', callback_data=f'last_app')
    return markup.add(btn1)

def reply_markup():
    markup = types.ReplyKeyboardMarkup(True, True)
    btn1 = types.KeyboardButton('Команды')
    return markup.add(btn1)
