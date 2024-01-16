from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext

import logging
import random
import re
import json
import html
from brainly_api import brainly
from telegram.constants import ParseMode

# Enable logging
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('myapp.log')

# set the logging level
logger.setLevel(logging.INFO)

# set the formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(handler)

# log a message
logger.info('Hello, world!')
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    # Send the welcome message with inline keyboard
    welcome_text = (
        "Halo! Aku bisa membantu kamu mencari jawaban di Brainly. "
        "Cukup ketikkan pertanyaanmu disini atau gunakan tombol inline dibawah! 😊"
    )

    # Create an array of inline buttons
    inline_buttons = [
        InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2"),
        InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu"),
        InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query="")
    ]

    # Create inline keyboard with adjusted size
    keyboard = InlineKeyboardMarkup.from_row(inline_buttons)

    # Send the message with inline keyboard to the group chat
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def jawab(update: Update, context: CallbackContext) -> None:
    await handle_message(update)

async def cari(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
       await handle_message(update)
    elif update.message.chat.type == 'private':
       await update.message.reply_text("Command hanya bisa digunakan di groups atau supergroups. 😅")

async def handle_inline(update: Update, context: CallbackContext) -> None:
    if len(update.inline_query.query) == 0:
        return

    inline_buttons = [
        InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2"),
        InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu"),
    ]

    # Add inline keyboard to the last result
    keyboard = InlineKeyboardMarkup.from_row(inline_buttons)

    # Check if the user has started the bot
    user_id = update.inline_query.from_user.id
    scrap = brainly(update.inline_query.query, 20)  # Fetch 20 questions
    results = []

    for i, selected in enumerate(scrap):
        question_text = f"<b>Pertanyaan:</b> {html.escape(selected.question.content)}\n"
        answer_text = f"{question_text}<b>Jawaban:</b> {html.escape(selected.answers[0].content)}\n"
        answer_text = re.sub(r'\n\s*\n', '\n', answer_text)
        combined_text = answer_text + question_text

        # Skip if the combined text exceeds 1024 characters
        if len(combined_text) > 1024:
            continue

        thumburl = selected.question.attachments[0].url if selected.question.attachments else None

        # Escape HTML special characters in the title
        escaped_title = f"Jawaban {i + 1} untuk: {html.escape(update.inline_query.query)}"

        # Define keyboard with url for longer answers
        if thumburl:
            result = {
                'type': 'photo',
                'id': str(i + 1),
                'photo_url': thumburl,
                'thumb_url': thumburl,
                'caption': combined_text,
                'parse_mode': 'HTML',
                'description': combined_text,
                'reply_markup':keyboard.to_dict()
            }
        else:
            result = {
                'type': 'article',
                'id': str(i + 1),
                'title': escaped_title,
                'input_message_content': {
                    'message_text': combined_text,
                    'parse_mode': 'HTML'
                },
                'description': combined_text,
                'reply_markup': keyboard.to_dict()
            }

        results.append(result)

    # Add a button for the channel link in the results
    await update.inline_query.answer(results)

async def handle_message(update: Update) -> None:
    answer_text = ''
    text = ''
    inline_buttons = [
                InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2"),
                InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu"),
                InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query="")
            ]
    keyboard = InlineKeyboardMarkup.from_row(inline_buttons)
    try:
        scrap = brainly(update.message.text, 50)
        selected = random.choice(scrap)

        text = f"*Pertanyaan:* {selected.question.content} \n"
        for i, answer in enumerate(selected.answers):
            text += f"\n*Jawaban {i + 1}:*\n{answer.content} \n"

        text = re.sub(r'\n\s*\n', '\n', text)
        text = text[:1024]
        text = re.sub(r'\\([^\\]+)\\', r'\1', text)
        text = text.replace('\\\\', '\\')
        text = re.sub(r'\\frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)', text)
        text = text.replace('*', '')
        text = text.replace('_', '')

        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

        for attachment in selected.question.attachments:
           await update.message.reply_photo(attachment.url, caption=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

        for answer in selected.answers:
            for attachment in answer.attachments:
                answer_text = f"*Jawaban:* {answer.content} \n"
                answer_text = re.sub(r'\n\s*\n', '\n', answer_text)
                answer_text = answer_text[:1024]
                answer_text = re.sub(r'\\([^\\]+)\\', r'\1', answer_text)
                answer_text = answer_text.replace('\\\\', '\\')
                answer_text = re.sub(r'\\frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)', answer_text)
                answer_text = text.replace('*', '')
                answer_text = text.replace('_', '')
                await update.message.reply_photo(attachment.url, caption=answer_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Answer Text: {answer_text}")
        print(f"Text: {text}")
        
def main() -> None:
    # Set up the Updater and pass it the bot's token
    updater = Updater(token='6453852810:AAGtLiSgkOa7nCBD7J0auGarPv1XEERQE8Q', use_context=True, request_kwargs={'read_timeout': 30, 'write_timeout': 30})

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.ChatType.PRIVATE, jawab))
    dp.add_handler(CommandHandler("cari", cari))

    # Register inline query handler
    dp.add_handler(InlineQueryHandler(handle_inline))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

    logger.info('Bot started. Press Ctrl+C to exit.')

if __name__ == '__main__':
   main()
