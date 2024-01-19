import telebot
from brainly_api import brainly
import random
import re
from telebot import types, time
import html
from urllib.parse import quote
import os, sys
import datetime
from requests.exceptions import ConnectionError, ReadTimeout

# Inisialisasi bot Telegram
bot_token = '6675489201:AAHZMqHMhPuhspPLkg4tQARAcPUqOuQkKZU'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Send the welcome message with inline keyboard
    welcome_text = (
        "Halo! Aku bisa membantu kamu mencari jawaban di Brainly. "
        "Cukup ketikkan pertanyaanmu disini atau gunakan tombol inline dibawah! 😊"
    )

    # Create an array of inline buttons
    inline_buttons = [
        types.InlineKeyboardButton("Channel 📢", url="https://t.me/aysbiz"),
        types.InlineKeyboardButton("Donate ☕", url="https://teer.id/farih_dzaky"),
        types.InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query="")
    ]

    # Create inline keyboard with adjusted size
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*inline_buttons)

    # Send the message with inline keyboard to the group chat
    bot.send_message(chat_id, welcome_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def jawab(message):
    handle_message(message)

@bot.inline_handler(lambda query: True)
def handle_inline(query):
    if len(query.query) == 0:
        return
    inline_buttons = [
        types.InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2"),
        types.InlineKeyboardButton("Donate ☕", url="https://teer.id/farih_dzaky"),
    ]

    # Add inline keyboard to the last result
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(*inline_buttons)
    # Check if the user has started the bot
    user_id = query.from_user.id
    scrap = brainly(query.query, 20)  # Fetch 20 questions
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
        escaped_title = f"Jawaban {i + 1} untuk: {html.escape(query.query)}"

        # Define keyboard with url for longer answers
        if thumburl:
            result = types.InlineQueryResultPhoto(
                id=str(i + 1),
                photo_url=thumburl,
                thumbnail_url=thumburl,
                caption=combined_text,
                parse_mode='HTML',
                description=combined_text,
                reply_markup=keyboard
            )
        else:
            result = types.InlineQueryResultArticle(
                id=str(i + 1),
                title=escaped_title,
                input_message_content=types.InputTextMessageContent(combined_text, parse_mode='HTML'),
                description=combined_text,
                reply_markup=keyboard
            )

        results.append(result)

    # Add a button for the channel link in the results

    bot.answer_inline_query(query.id, results)

def handle_message(message):
    answer_text = ''
    text = ''
    inline_buttons = [
                types.InlineKeyboardButton("Channel 📢", url="https://t.me/nekozu2"),
                types.InlineKeyboardButton("Donate ☕", url="https://teer.id/farih_dzaky"),
                types.InlineKeyboardButton("Gunakan Inline 🚀", switch_inline_query="")
            ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*inline_buttons)
    try:
        scrap = brainly(message.text, 50)
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

        message_sent = bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

        for attachment in selected.question.attachments:
            bot.send_photo(message.chat.id, attachment.url, caption=text, parse_mode='Markdown', reply_markup=keyboard)

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
                bot.send_photo(message.chat.id, attachment.url, caption=answer_text, parse_mode='Markdown', reply_markup=keyboard)

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Answer Text: {answer_text}")
        print(f"Text: {text}")

while True:
    try:
        bot.polling(none_stop=True, timeout=90)
    except Exception as e:
        print(datetime.datetime.now(), e)
        time.sleep(5)
        continue
