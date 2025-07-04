import logging
import os
import requests
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler, CallbackQueryHandler)

TOKEN = '7008848539:AAGUrtKbnIe50r45YRxBFzG9B4kKR-csxiA'
PEXELS_API_KEY = 'kQdIkN07IqZI7byq9g2H4GbRbYH7m5JCdGXjaYznNbh0ekFxadxE4wcW'
ADMIN_ID = 6924443594

LOG_FILE = 'log.txt'
USER_FILE = 'users.txt'

CHOOSE_LANG, ASK_QUERY, ASK_AMOUNT = range(3)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=LOG_FILE
)

def register_user(user):
    user_info = f"{user.id} | {user.first_name} {user.last_name or ''} | @{user.username}\n"
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            f.write(user_info)
    else:
        with open(USER_FILE, 'r') as f:
            users = f.read()
        if str(user.id) not in users:
            with open(USER_FILE, 'a') as f:
                f.write(user_info)

def is_admin(user_id):
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data='uz')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='en')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please select a language:", reply_markup=reply_markup)
    return CHOOSE_LANG

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data
    context.user_data['lang'] = lang

    texts = {
        'uz': "Qanday rasm qidiryapsiz?",
        'ru': "Какое изображение вы ищете?",
        'en': "What image are you looking for?"
    }
    await query.edit_message_text(texts.get(lang, "What image are you looking for?"))
    return ASK_QUERY

async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    context.user_data['query'] = update.message.text

    texts = {
        'uz': "Nechta rasm yuborishimni hohlaysiz? (Masalan: 5)",
        'ru': "Сколько изображений отправить? (например: 5)",
        'en': "How many images do you want? (e.g., 5)"
    }
    await update.message.reply_text(texts.get(lang))
    return ASK_AMOUNT

async def send_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    query = context.user_data.get('query')

    try:
        amount = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Iltimos, faqat son kiriting.")
        return ASK_AMOUNT

    url = f"https://api.pexels.com/v1/search?query={query}&per_page={amount}"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200 or 'photos' not in response.json():
        await update.message.reply_text("Rasmlar topilmadi.")
        return ASK_QUERY   # 👉 Yana so‘rovni qaytaramiz

    photos = response.json()['photos']

    for photo in photos:
        img_url = photo['src']['large2x']
        await update.message.reply_photo(photo=img_url)

    finish_texts = {
        'uz': "✅ Rasmlar yuborildi!\n\nYana qanday rasm qidiramiz? 🔎",
        'ru': "✅ Изображения отправлены!\n\nЧто ещё ищем? 🔎",
        'en': "✅ Images sent!\n\nWhat else are you looking for? 🔎"
    }

    await update.message.reply_text(finish_texts.get(lang))
    return ASK_QUERY   # 👉 To‘xtatmay yana so‘rovga qaytamiz


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
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
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, handle_media))

    app.run_polling()

if __name__ == '__main__':
    main()
