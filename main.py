###imports

import sqlite3 as sql
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup 
from telegram import Update 
from telegram import KeyboardButton 
from telegram import ReplyKeyboardRemove 
from telegram.ext import Application
from telegram.ext import CommandHandler 
from telegram.ext import MessageHandler 
from telegram.ext import CallbackQueryHandler 
from telegram.ext import ContextTypes
from telegram.ext import filters 


##values

ADMIN_ID = 6025545911

###token 

BOT_TOKEN = "9122995845:AAECYiJYrgP-tVGmSJqtmSKdA2VZd_6BqCQ"

if BOT_TOKEN == "" :
    print("Please enter a bot token and rerunning")
    exit()


###app 

app = Application.builder().token(BOT_TOKEN).build()


###database 

cnon = sql.connect("Bot_1.db")
cur = cnon.cursor()

##create table for users in database => this table can save name, user_name, user_id and phone_number.
cur.execute("""
CREATE TABLE IF NOT EXISTS users(name TEXT ,user_name TEXT , user_id INTEGER PRIMARY KEY ,phone_number TEXT)
""")
cnon.commit()


##this is a def for read phone_number from users table.
def r_phone (user_id) :
    cur.execute("""
    SELECT phone_number FROM users WHERE user_id  = ?
    """, (user_id,))
    result = cur.fetchone()
    if result is None :
        return None 
    return result[0]


##this def do read user information from database.
def r_user(value):
    if value.isdigit():
        cur.execute("""
        SELECT * FROM users
        WHERE user_id = ?
        """, (int(value),))
    else:
        value = value.lstrip("@")
        cur.execute("""
        SELECT * FROM users
        WHERE user_name = ?
        """, (value,))
    return cur.fetchone()
    

##this is a def for write phone_number in users table.
def w_phone (user_id, phone_number) :
    cur.execute("""
    UPDATE users SET phone_number = ? WHERE user_id = ?
    """, (phone_number, user_id))
    cnon.commit()


##this is for save user information in users table.
def w_user (name, user_name, user_id) :
    cur.execute("""
    INSERT INTO users(name, user_name, user_id)
    VALUES(?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
    name = excluded.name,
    user_name = excluded.user_name
    """, (name, user_name, user_id))
    cnon.commit()


##this is for get phone_number with a KeyboardButton from user.
def k_phone () :
    button = KeyboardButton("ارسال شماره‌تلفن", request_contact = True)
    return ReplyKeyboardMarkup([[button]], resize_keyboard = True, one_time_keyboard = True)


##this def do take phone_number from telegram.
async def get_phone (update, context) :
    contact = update.message.contact
    if contact is None :
        return
    if contact.user_id != update.effective_user.id :
        await update.message.reply_text("برای شروع، شماره‌تلفن خود را با استفاده از دکمه مشخص شده، برای ما ارسال کنید.")
        return
    user_id = update.effective_user.id 
    phone_number = contact.phone_number
    #here do it save phone_number in database and users table.
    w_phone(user_id, phone_number)
    await update.message.reply_text(
        "شماره‌تلفن شما با موفقیت در دیتابیس ربات ذخیره شد.",
        reply_markup = ReplyKeyboardRemove()
    )


##defs

async def started (update, context) :
    name = update.effective_user.first_name
    user_name = update.effective_user.username
    user_id = update.effective_user.id

    w_user(name, user_name, user_id)

    text = f"درود {name}.\nکیر شدی، شمارتو گرفتم."
    await update.message.reply_text(
        text,
        reply_markup = k_phone()
    )


##this is a def for admin and find user info.
async def a_search(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    value = update.message.text.strip()
    user = r_user(value)

    if user is None:
        await update.message.reply_text(
            "اطلاعات کاربر در دیتابیس وجود ندارد."
        )
        return

    name = user[0]
    user_name = user[1]
    user_id = user[2]
    phone_number = user[3]

    text = f"""
اطلاعات کاربر:

اسم: {name}
نام کاربری: {user_name}
آیدی: {user_id}
شماره تلفن: {phone_number}
"""
    await update.message.reply_text(text)


###handlers

##get_phone handler
app.add_handler(CommandHandler("start", started))

##started handler
app.add_handler(MessageHandler(filters.CONTACT, get_phone))

##a_search
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, a_search))


##running

print("Bot is on.")
app.run_polling()
