from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes

OWNER_ID = 762204827  # твой Telegram ID

message_mapping = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_username = (await context.bot.get_me()).username
    personal_link = f"https://t.me/{bot_username}?start={user.id}"

    welcome_message = (
        "Привет! Задай мне любой вопрос анонимно, и жди ответ! 👇\n"
        f"А вот твоя уникальная ссылка:\n{personal_link}"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if user.id == OWNER_ID and msg.reply_to_message:
        original_id = msg.reply_to_message.message_id
        if original_id in message_mapping:
            recipient_id = message_mapping[original_id]
            await context.bot.copy_message(chat_id=recipient_id, from_chat_id=msg.chat.id, message_id=msg.message_id)
            await msg.reply_text("✅ Ответ отправлен.")
        else:
            await msg.reply_text("❗ Не удалось найти получателя.")
    elif user.id != OWNER_ID:
        # Отправка вопроса владельцу
        info = f"📩 *Получен новый вопрос!*\n"
        if user.username:
            info += f"_Вопрос задал(а): @{user.username}_\n"
        else:
            info += "_(Без имени)_\n"

        if msg.text:
            sent = await context.bot.send_message(chat_id=OWNER_ID, text=f"{info}\n{msg.text}", parse_mode="Markdown")
        elif msg.photo:
            file_id = msg.photo[-1].file_id
            caption = msg.caption or ""
            sent = await context.bot.send_photo(chat_id=OWNER_ID, photo=file_id, caption=f"{info}\n{caption}", parse_mode="Markdown")
        elif msg.video:
            file_id = msg.video.file_id
            caption = msg.caption or ""
            sent = await context.bot.send_video(chat_id=OWNER_ID, video=file_id, caption=f"{info}\n{caption}", parse_mode="Markdown")
        else:
            sent = await context.bot.send_message(chat_id=OWNER_ID, text=info, parse_mode="Markdown")

        # Для отправителя — просто подтверждение
        await msg.reply_text("✅ Вопрос отправлен. Жди ответа!")
        message_mapping[sent.message_id] = user.id
    else:
        await msg.reply_text("Ответьте на сообщение, чтобы ответ отправился.")

if __name__ == '__main__':
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен.")
    app.run_polling()
