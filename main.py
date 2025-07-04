# ImgFlow Bot - Full Version with Admin Features

import logging
import os
import requests
from collections import Counter
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
    ConversationHandler, CallbackQueryHandler
)

TOKEN = '7008848539:AAGUrtKbnBFzG9B4kKR-csxiA'  
PEXELS_API_KEY = 'kQdIkN07Iqg2H4GbRbYH7m5JCdGXjaYznNbh0ekFxadxE4wcW'  
ADMIN_ID = 69244

LOG_FILE = 'log.txt'
USER_FILE = 'users.txt'
QUERY_FILE = 'queries.txt'
BANNED_FILE = 'banned.txt'

CHOOSE_LANG, ASK_QUERY, ASK_AMOUNT = range(3)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=LOG_FILE
)

# Utils

def register_user(user):
    user_info = f"{user.id} | {user.first_name} {user.last_name or ''} | @{user.username}\n"
    if not os.path.exists(USER_FILE) or str(user.id) not in open(USER_FILE).read():
        with open(USER_FILE, 'a') as f:
            f.write(user_info)


def is_admin(user_id):
    return user_id == ADMIN_ID


def is_banned(user_id):
    if not os.path.exists(BANNED_FILE):
        return False
    return str(user_id) in open(BANNED_FILE).read()

# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id):
        await update.message.reply_text("⛔ Siz ban qilingansiz.")
        return ConversationHandler.END

    register_user(user)

    keyboard = [
        [InlineKeyboardButton("\ud83c\uddfa\ud83c\uddff O'zbek", callback_data='uz')],
        [InlineKeyboardButton("\ud83c\uddf7\ud83c\uddfa \u0420\u0443\u0441\u0441\u043a\u0438\u0439", callback_data='ru')],
        [InlineKeyboardButton("\ud83c\uddec\ud83c\udde7 English", callback_data='en')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Iltimos, tilni tanlang:", reply_markup=reply_markup)
    return CHOOSE_LANG


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['lang'] = query.data

    texts = {
        'uz': "Qanday rasm qidiryapsiz?",
        'ru': "Какое изображение вы ищете?",
        'en': "What image are you looking for?"
    }
    await query.edit_message_text(texts.get(query.data, "What image?"))
    return ASK_QUERY


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['query'] = update.message.text
    with open(QUERY_FILE, 'a') as f:
        f.write(f"{update.effective_user.id}|{update.message.text}\n")

    lang = context.user_data.get('lang', 'uz')
    prompts = {
        'uz': "Nechta rasm yuborishimni hohlaysiz?",
        'ru': "Сколько изображений отправить?",
        'en': "How many images do you want?"
    }
    await update.message.reply_text(prompts.get(lang))
    return ASK_AMOUNT


async def send_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = context.user_data.get('query')
    try:
        amount = int(update.message.text)
    except:
        await update.message.reply_text("❗ Faqat son kiriting.")
        return ASK_AMOUNT

    url = f"https://api.pexels.com/v1/search?query={query}&per_page={amount}"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)

    photos = response.json().get('photos', [])
    for photo in photos:
        await update.message.reply_photo(photo=photo['src']['large2x'])

    await update.message.reply_text("✅ Yuborildi! Yana so'rov bering.")
    return ASK_QUERY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END


async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'rb') as f:
                await update.message.reply_document(document=InputFile(f, filename="log.txt"))
        else:
            await update.message.reply_text("Log fayli topilmadi.")
    else:
        await update.message.reply_text("Sizda ruxsat yo‘q.")

# Foydalanuvchilar ro'yxatini yuborish + foydalanuvchilar soni
async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                users = f.readlines()
                user_count = len(users)  # 📊 Foydalanuvchilar sonini hisoblash

            # Faylni yuborish
            with open(USER_FILE, 'rb') as f:
                await update.message.reply_document(InputFile(f, filename="users.txt"))

            # Sonini yozish
            await update.message.reply_text(f"👥 Umumiy foydalanuvchilar soni: {user_count} ta")
        else:
            await update.message.reply_text("❌ Foydalanuvchilar ro'yxati topilmadi.")
    else:
        await update.message.reply_text("⛔ Sizda ruxsat yo'q.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    with open(USER_FILE, 'r') as f:
        users = [line.split('|')[0].strip() for line in f]

    message = update.message.text.replace('/broadcast', '').strip()

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
        except:
            continue

    await update.message.reply_text("Xabar yuborildi.")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    with open(USER_FILE, 'r') as f:
        users = [line.split('|')[0].strip() for line in f]

    file_id = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        send_fn = context.bot.send_photo
        arg_name = 'photo'
    elif update.message.video:
        file_id = update.message.video.file_id
        send_fn = context.bot.send_video
        arg_name = 'video'
    elif update.message.voice:
        file_id = update.message.voice.file_id
        send_fn = context.bot.send_voice
        arg_name = 'voice'
    elif update.message.document:
        file_id = update.message.document.file_id
        send_fn = context.bot.send_document
        arg_name = 'document'
    else:
        await update.message.reply_text("Fayl yuboring.")
        return

    for user_id in users:
        try:
            await send_fn(chat_id=int(user_id), **{arg_name: file_id})
        except:
            continue

    await update.message.reply_text("Media yuborildi.")


async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        open(LOG_FILE, 'w').close()
        await update.message.reply_text("🗑 Loglar tozalandi.")


async def clear_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        open(USER_FILE, 'w').close()
        await update.message.reply_text("🗑 Foydalanuvchilar tozalandi.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        users = open(USER_FILE).readlines() if os.path.exists(USER_FILE) else []
        queries = open(QUERY_FILE).readlines() if os.path.exists(QUERY_FILE) else []
        counter = Counter([q.split('|')[1].strip() for q in queries])
        top = "\n".join([f"{k} - {v}x" for k, v in counter.most_common(3)])
        await update.message.reply_text(f"👥 {len(users)} users\n🔍 {len(queries)} queries\n🔥 Top queries:\n{top}")


async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        user_id = context.args[0]
        with open(BANNED_FILE, 'a') as f:
            f.write(f"{user_id}\n")
        await update.message.reply_text(f"⛔ User {user_id} banned.")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        user_id = context.args[0]
        lines = open(BANNED_FILE).readlines()
        with open(BANNED_FILE, 'w') as f:
            for line in lines:
                if user_id not in line:
                    f.write(line)
        await update.message.reply_text(f"✅ User {user_id} unbanned.")


# Main

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_LANG: [CallbackQueryHandler(choose_language)],
            ASK_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount)],
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_images)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("getlogs", get_logs))
    app.add_handler(CommandHandler("getusers", get_users))
    app.add_handler(CommandHandler("clearlogs", clear_logs))
    app.add_handler(CommandHandler("clearusers", clear_users))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.run_polling()

if __name__ == '__main__':
    main()
