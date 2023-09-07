import telebot
import re
from telebot import types
import pymysql as sql
from config import host, user, password, db_name

pattern = "[0-9]"

connection = sql.connect(
    host=host,
    user=user,
    password=password, 
    database=db_name, 
    port=3306
)
cursor = connection.cursor()

bot = telebot.TeleBot('6444064096:AAFxjjhp3yxf2vwWhDFJmI17HeGBkSGlF_A')

# Система рейтинга

@bot.message_handler(commands=['loster'])
def bot_active(message):
    msg = "SELECT * FROM server where id = "+str(message.chat.id)+";"
    exCUTE = cursor.execute(msg)
    if(exCUTE==0):
        bot.send_message(message.chat.id, "Бот запомнил этот сервер!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True))
        msg = "INSERT INTO `server` (`id`) VALUES ('"+ str(message.chat.id) +"');"
        cursor.execute(msg)
        connection.commit()
        return 0
    bot.send_message(message.chat.id, "Бот уже знает этот сервер!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True))
    return 0


def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Создать объявление!")
    markup.row(button)
    bot.send_message(message.chat.id, "Привет, что-то потерял?", reply_markup=markup)
    bot.register_next_step_handler(message, typeSellector)

def typeSellector(message):
    if (message.text == "Создать объявление!" or message.text == "Перегенерировать объявление." or message.text == "Создать ещё одно объявление!"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Школьный предмет")
        button2 = types.KeyboardButton("Личный предмет")
        markup.row(button1, button2)  
        bot.send_message(message.chat.id ,"Выберите тип предмета:", reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)
        
    elif (message.text == "Школьный предмет" or message.text == "Личный предмет"):
        if (message.text == "Школьный предмет"):
            itemTemp = "Учебник биологии"
            msg = "UPDATE user SET itemtype = 'школьный' WHERE id = '"+ str(message.from_user.id) +"';"
        elif (message.text == "Личный предмет"):
            itemTemp = "Зарядка Type-C"
            msg = "UPDATE user SET itemtype = 'личный' WHERE id = '"+ str(message.from_user.id) +"';"
        cursor.execute(msg)
        connection.commit()
        bot.send_message(message.chat.id, 'Введите название предмета:\nПример: "'+ itemTemp +'".', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, itemName)

    elif (message.text == "Всё верно!"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Создать ещё одно объявление!")
        markup.row(button)
        msg = "SELECT username FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        userNameStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")+" ("+ message.from_user.first_name +")"
        msg = "SELECT itemtype FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemTypeStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT itemname FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemNameStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT itemussage FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemUssageStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT userauditory FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        userAuditoryStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        form = "Привет, меня зовут: *" + userNameStr + "*, и я ищу *" + itemTypeStr + "* предмет под названием: '*" + itemNameStr + "*' на *" + itemUssageStr + "* минут.\nЕсли у кого то он есть, то прошу передать в *" + userAuditoryStr + "* аудиторию."
        msg = "SELECT * FROM server;"
        exCUTE = cursor.execute(msg)
        botServers = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").split(" ")
        for i in range(len(botServers)):
            bot.send_message(botServers[i], form, parse_mode= 'Markdown')
        bot.send_message(message.chat.id, 'Отправляю объявление.', reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)

    else:
        bot.send_message(message.chat.id, 'Вы ввели что-то вместо выбора кнопки.\nНапишите "/start" или "старт" чтобы использовать бота заново.', reply_markup=types.ReplyKeyboardRemove())

        
def itemName(message):
    msg = "UPDATE user SET itemname = '"+ message.text +"' WHERE id = '"+ str(message.from_user.id) +"';"
    cursor.execute(msg)
    connection.commit()
    bot.send_message(message.chat.id, 'Введите имя пользователя:\nПример: "Иванов Иван".')
    bot.register_next_step_handler(message, userName)

def userName(message):
    msg = "UPDATE user SET username = '"+ message.text +"' WHERE id = '"+ str(message.from_user.id) +"';"
    cursor.execute(msg)
    connection.commit()
    bot.send_message(message.chat.id, 'Введите время пользования предмета:\nПример: "30" = 30 минут.')
    bot.register_next_step_handler(message, itemUssage)

def itemUssage(message):
    if (not bool(re.match(pattern, message.text))):
        bot.send_message(message.chat.id, 'Введите *ЧИСЛО*:\nПример: "30" = 30 минут.', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, itemUssage)
    else:
        msg = "UPDATE user SET itemussage = '"+ message.text +"' WHERE id = '"+ str(message.from_user.id) +"';"
        cursor.execute(msg)
        connection.commit()       
        bot.send_message(message.chat.id, 'Введите номер аудитории:\nПример: "114" = 114 аудитория.')
        bot.register_next_step_handler(message, userAuditory)

def userAuditory(message):
    if (not bool(re.match(pattern, message.text))):
        bot.send_message(message.chat.id, 'Введите *ЧИСЛО*:\nПример: "114" = 114 аудитория.', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, userAuditory)
    else:  
        msg = "UPDATE user SET userauditory = '"+ message.text +"' WHERE id = '"+ str(message.from_user.id) +"';"
        cursor.execute(msg)
        connection.commit()
        msg = "SELECT username FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        userNameStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")+" ("+ message.from_user.first_name +")"
        msg = "SELECT itemtype FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemTypeStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT itemname FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemNameStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT itemussage FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        itemUssageStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        msg = "SELECT userauditory FROM user WHERE id = "+ str(message.from_user.id) +";"
        cursor.execute(msg)
        userAuditoryStr = str(cursor.fetchall()).replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        form = "Привет, меня зовут: *" + userNameStr + "*, и я ищу *" + itemTypeStr + "* предмет под названием: '*" + itemNameStr + "*' на *" + itemUssageStr + "* минут.\nЕсли у кого то он есть, то прошу передать в *" + userAuditoryStr + "* аудиторию."
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Всё верно!")
        button2 = types.KeyboardButton("Перегенерировать объявление.")
        markup.row(button1, button2)
        bot.send_message(message.chat.id, "Ваше объявление выглядит так:\n\n" + form + "\n\nВсё верно?", parse_mode= 'Markdown', reply_markup=markup)
        bot.register_next_step_handler(message, typeSellector)

@bot.message_handler()
def any_message(message):
    msg = "SELECT * FROM user where id = "+str(message.from_user.id)
    exCUTE = cursor.execute(msg)
    if(exCUTE==0):
        msg = "INSERT INTO `user` (`id`, `username`, `itemtype`, `itemname`, `itemussage`, `userauditory`, `userrate`) VALUES ('"+ str(message.from_user.id) +"', '"+ message.from_user.first_name +"', '-', '-', '0', '0', '0');"
        cursor.execute(msg)
        connection.commit()
    if(message.text=="Создать ещё одно объявление!"):
        typeSellector(message)
    elif((message.text).lower()=="старт" or (message.text).lower()=="/start"):
        temp = message
        temp.text = "/start"
        main(temp)

bot.infinity_polling()