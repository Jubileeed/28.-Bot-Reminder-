import telebot
import schedule
import time
from threading import Thread
import pytz
from datetime import datetime

# Ваш токен от BotFather
API_TOKEN = 'YOUR_API_TOKEN'

bot = telebot.TeleBot(API_TOKEN)

# Хранилище для напоминаний
reminders = []

# Московский часовой пояс
MOSCOW_TIMEZONE = 'Europe/Moscow'

# Функция для отправки напоминания
def send_reminder(chat_id, text):
    bot.send_message(chat_id, text)

# Функция для планирования напоминания с учетом московского времени
def schedule_reminder(chat_id, text, reminder_time):
    reminders.append({
        'chat_id': chat_id,
        'text': text,
        'time': reminder_time
    })

    # Конвертируем время напоминания в UTC для корректного запуска
    user_timezone = pytz.timezone(MOSCOW_TIMEZONE)
    reminder_datetime = datetime.strptime(reminder_time, '%H:%M').time()
    now = datetime.now(user_timezone)
    reminder_datetime = datetime.combine(now.date(), reminder_datetime)
    reminder_utc = user_timezone.localize(reminder_datetime).astimezone(pytz.utc)

    schedule.every().day.at(reminder_utc.strftime('%H:%M')).do(send_reminder, 
chat_id, text)
    bot.send_message(chat_id, f"Напоминание установлено на {reminder_time} 
по московскому времени")

# Команда для установки напоминания
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_reminder_button = telebot.types.KeyboardButton('Создать напоминание')
    markup.add(create_reminder_button)
    bot.send_message(message.chat.id, "Привет! Я бот для создания напоминаний. 
Нажмите 'Создать напоминание', чтобы установить новое напоминание.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Создать напоминание')
def set_reminder(message):
    try:
        msg = bot.send_message(message.chat.id, "Введите время напоминания в 
формате ЧЧ:ММ по московскому времени:")
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
