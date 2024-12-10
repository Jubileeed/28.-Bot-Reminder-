import telebot
import schedule
import time
from threading import Thread
from telebot import types

# Ваш токен от BotFather
API_TOKEN = 'YOUR_BOT_API_TOKEN'

bot = telebot.TeleBot(API_TOKEN)

# Хранилище для напоминаний
reminders = []

# Функция для отправки напоминания
def send_reminder(chat_id, text):
    bot.send_message(chat_id, text)

# Функция для планирования напоминания
def schedule_reminder(chat_id, text, reminder_time):
    reminders.append({
        'chat_id': chat_id,
        'text': text,
        'time': reminder_time
    })
    schedule.every().day.at(reminder_time).do(send_reminder, chat_id, text)
    bot.send_message(chat_id, f"Напоминание установлено на {reminder_time}")

# Команда для установки напоминания с кнопкой
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Создать напоминание")
    keyboard.add(button)
    bot.send_message(message.chat.id, "Нажмите кнопку ниже, чтобы создать напоминание:", reply_markup=keyboard)


# Обработчик нажатия на кнопку "Создать напоминание"
@bot.message_handler(func=lambda message: message.text == "Создать напоминание")
def set_reminder(message):
    try:
        msg = bot.send_message(message.chat.id, "Введите время напоминания в формате ЧЧ:ММ:")
        bot.register_next_step_handler(msg, get_time)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Получаем время и запрашиваем текст напоминания
def get_time(message):
    reminder_time = message.text
    msg = bot.send_message(message.chat.id, "Введите текст напоминания:")
    bot.register_next_step_handler(msg, get_text, reminder_time)

# Получаем текст и создаем напоминание
def get_text(message, reminder_time):
    reminder_text = message.text
    chat_id = message.chat.id
    schedule_reminder(chat_id, reminder_text, reminder_time)

# Фоновая функция для выполнения задач по расписанию
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск фоновой задачи
def run_schedule():
    Thread(target=schedule_checker).start()

if __name__ == '__main__':
    run_schedule()
    bot.polling(none_stop=True)
