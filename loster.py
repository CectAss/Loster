import telebot
import re
from telebot import types

itemTypeBool = True
itemNameStr = ""
itemUssageInt = 0
userAuditoryInt = 0
userNameStr = ""

botServers = []
form = ""
pattern = "[0-9]"

bot = telebot.TeleBot('6444064096:AAFxjjhp3yxf2vwWhDFJmI17HeGBkSGlF_A')

# Система рейтинга

@bot.message_handler(commands=['loster'])
def bot_active(message):
    global botServers
    for i in range(len(botServers)):
        if(message.chat.id==botServers[i]):
            bot.send_message(message.chat.id, "Бот уже знает этот сервер!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True))
            return 0
    bot.send_message(message.chat.id, "Бот запомнил этот сервер!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True))
    botServers.append(message.chat.id)

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Создать объявление!")
    markup.row(button)
    bot.send_message(message.chat.id, "Привет, что-то потерял?", reply_markup=markup)
    bot.register_next_step_handler(message, typeSellector)

def typeSellector(message):
    global botServers
    global itemTypeBool
    if (message.text == "Создать объявление!" or message.text == "Перегенерировать объявление." or message.text == "Создать ещё одно объявление!"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Школьный предмет")
        button2 = types.KeyboardButton("Личный предмет")
        markup.row(button1, button2)  
        bot.send_message(message.chat.id ,"Выберите тип предмета:", reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)
    elif (message.text == "Школьный предмет" or message.text == "Личный предмет"):
        if (message.text == "Школьный предмет"):
            itemTypeBool=True
            itemTemp = "Учебник биологии"
        elif (message.text == "Личный предмет"):
            itemTypeBool=False
            itemTemp = "Зарядка Type-C"
        bot.send_message(message.chat.id, 'Введите название предмета:\nПример: "'+ itemTemp +'".', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, itemName)
    elif (message.text == "Всё верно!"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Создать ещё одно объявление!")
        markup.row(button)
        for i in range(len(botServers)):
            bot.send_message(botServers[i], form, parse_mode= 'Markdown')
        bot.send_message(message.chat.id, 'Отправляю объявление.', reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)
    else:
        bot.send_message(message.chat.id, 'Вы ввели что-то вместо выбора кнопки.\nНапишите "/start" или "старт" чтобы использовать бота заново.', reply_markup=types.ReplyKeyboardRemove())

        
def itemName(message):
    global itemNameStr
    global pattern
    itemNameStr = message.text
    bot.send_message(message.chat.id, 'Введите имя пользователя:\nПример: "Иванов Иван".')
    bot.register_next_step_handler(message, userName)

def userName(message):
    global userNameStr
    userNameStr = message.text + " ("+ message.from_user.first_name +")"
    bot.send_message(message.chat.id, 'Введите время пользования предмета:\nПример: "30" = 30 минут.')
    bot.register_next_step_handler(message, itemUssage)

def itemUssage(message):
    global itemUssageInt
    if (not bool(re.match(pattern, message.text))):
        bot.send_message(message.chat.id, 'Введите *ЧИСЛО*:\nПример: "30" = 30 минут.', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, itemUssage)
    else:
        itemUssageInt = int(message.text)
        bot.send_message(message.chat.id, 'Введите номер аудитории:\nПример: "114" = 114 аудитория.')
        bot.register_next_step_handler(message, userAuditory)

def userAuditory(message):
    global userNameStr
    global userAuditoryInt
    global form
    global itemTypeBool
    if (not bool(re.match(pattern, message.text))):
        bot.send_message(message.chat.id, 'Введите *ЧИСЛО*:\nПример: "114" = 114 аудитория.', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, userAuditory)
    else:  
        userAuditoryInt = int(message.text)
        typeer = ""
        if (itemTypeBool):
            typeer = "школьный"
        else: 
            typeer = "личный"
        form = "Привет, меня зовут: *" + userNameStr + "*, и я ищу *" + typeer + "* предмет под названием: '*" + itemNameStr.lower() + "*' на *" + str(itemUssageInt) + "* минут.\nЕсли у кого то он есть, то прошу передать в *" + str(userAuditoryInt) + "* аудиторию."
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Всё верно!")
        button2 = types.KeyboardButton("Перегенерировать объявление.")
        markup.row(button1, button2)
        bot.send_message(message.chat.id, "Ваше объявление выглядит так:\n\n" + form + "\n\nВсё верно?", parse_mode= 'Markdown', reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)

@bot.message_handler()
def any_message(message):
    if(message.text=="Создать ещё одно объявление!"):
        typeSellector(message)
    elif((message.text).lower()=="старт"):
        temp = message
        temp.text = "/start"
        main(temp)

bot.infinity_polling()
