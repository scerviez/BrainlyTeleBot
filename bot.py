from brainly_api import brainly
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultPhoto
import random
import re
import html
from pyrogram import enums

# Inisialisasi bot Telegram
api_id = 'api id kamu'
api_hash = 'api hash kamu'
bot_token = 'bot token kamu'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
def start(client, message):
    chat_id = message.chat.id
    welcome_text = (
        "Halo! Aku bisa membantu kamu mencari jawaban di Brainly. "
        "Cukup ketikkan pertanyaanmu disini atau gunakan tombol inline dibawah! 😊"
    )
    inline_keyboard = [
        [InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2")],
        [InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu/goal?g=0")],
        [InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query_current_chat="")],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    client.send_message(chat_id, welcome_text, reply_markup=reply_markup)

@app.on_message(filters.private)
def answer_query(client, message):
    handle_message(client, message)

@app.on_inline_query()
def inline_query_handler(client, inline_query):
    query = inline_query.query
    user_id = inline_query.from_user.id
    if query == "":
        return
    
    results = brainly(query, 20)  # Adjust the number of results if needed
    answers = []
    inline_keyboard = [
            [InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2")],
            [InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu/goal?g=0")],
        ]
        
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    for i, selected in enumerate(results):
        question_text = f"<b>Pertanyaan:</b> {html.escape(selected.question.content)}\n"
        answer_text = f"{question_text}<b>Jawaban:</b> {html.escape(selected.answers[0].content)}\n"
        answer_text = re.sub(r'\n\s*\n', '\n', answer_text)
        combined_text = answer_text + question_text
        
        if len(combined_text) > 1024:
            continue
        
        thumb_url = selected.question.attachments[0].url if selected.question.attachments else None
        escaped_title = f"Jawaban {i + 1} untuk: {html.escape(query)}"
        
        if thumb_url:
            single_result = InlineQueryResultPhoto(
                id=str(i),
                photo_url=thumb_url,
                thumb_url=thumb_url,
                caption=combined_text,
                title=escaped_title,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            single_result = InlineQueryResultArticle(
                id=str(i),
                title=escaped_title,
                input_message_content=InputTextMessageContent(combined_text, parse_mode=enums.ParseMode.HTML),
                description=combined_text,
                reply_markup=reply_markup
            )
        answers.append(single_result)

    client.answer_inline_query(inline_query.id, results=answers)

def handle_message(client, message):
    try:
        scrap = brainly(message.text, 50)  # You may want to adjust the number here too
        selected = random.choice(scrap)

        text = f"*Pertanyaan:* {selected.question.content} \n\n"
        for i, answer in enumerate(selected.answers):
            text += f"*Jawaban {i + 1}:*\n{answer.content}\n\n"

        text = re.sub(r'\n\s*\n', '\n', text)
        text = text[:4096]  # Truncate to max message length if necessary
        text = re.sub(r'\\([^\\]+)\\', r'\1', text)
        text = text.replace('\\\\', '\\')
        text = re.sub(r'\\frac\{(.*?)\}\{(.*?)\}', r'(\1)/(\2)', text)
        text = text.replace('*', '')
        text = text.replace('_', '')

        inline_keyboard = [
            [InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2")],
            [InlineKeyboardButton("Donate ☕", url="https://ko-fi.com/nekozu/goal?g=0")],
            [InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query_current_chat="")],
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        thumb_url = selected.question.attachments[0].url if selected.question.attachments else None
        if thumb_url:
            client.send_photo(message.chat.id, photo=thumb_url, caption=text, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            client.send_message(message.chat.id, text, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=reply_markup)

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Answer Text: {text}")
        print(f"Text: {text}")

# Add the following line if you want the bot to continuously run
app.run()
