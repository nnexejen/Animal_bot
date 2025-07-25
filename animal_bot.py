# Импорт необходимых библиотек
import logging  # Для логирования событий и ошибок
import os  # Для работы с переменными окружения
import requests  # Для выполнения HTTP-запросов к API
from telegram import ReplyKeyboardMarkup  # Для создания кнопок в Telegram
from telegram.ext import CommandHandler, Updater  # Для обработки команд и работы с Telegram Bot API
from dotenv import load_dotenv  # Для загрузки переменных из файла .env

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена бота из переменной окружения, если не найдено - используется значение по умолчанию
secret_token = os.getenv('TOKEN', default='123')

# Настройка логирования для отслеживания событий и ошибок
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат логов
    level=logging.INFO  # Уровень логирования (INFO и выше)
)

# URL-адреса API для получения случайных изображений котов и собак
CAT_URL = os.getenv('CAT_URL', default='https://api.thecatapi.com/v1/images/search')  # API для котов
DOG_URL = os.getenv('DOG_URL', default='https://api.thedogapi.com/v1/images/search')  # API для собак

# Функция для получения URL случайного изображения животного
def get_new_image(URL):
    try:
        # Выполнение GET-запроса к переданному URL API
        response = requests.get(URL)
    except Exception as error:
        # Логирование ошибки, если запрос к API не удался
        logging.error(f'Ошибка при запросе к основному API: {error}')
        # В случае ошибки используется запасной API (для собак)
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    # Парсинг ответа API в формате JSON
    response = response.json()
    # Извлечение URL изображения из ответа
    random_animal = response[0].get('url')
    return random_animal

# Универсальная функция для отправки изображения животного (кота или собаки)
def new_animal(update, context, animal, url):
    # Получение объекта чата из обновления
    chat = update.effective_chat
    # Получение имени пользователя
    name = update.message.chat.first_name
    # Получение URL изображения через функцию get_new_image
    image = get_new_image(url)
    # Логирование события отправки изображения
    logging.info(f'Отправлен {animal} {image} для {name}')
    # Отправка изображения в чат
    context.bot.send_photo(chat.id, image)

# Функция-обработчик команды /newcat для отправки изображения кота
def new_cat(update, context):
    new_animal(update, context, 'котик', CAT_URL)

# Функция-обработчик команды /newdog для отправки изображения собаки
def new_dog(update, context):
    new_animal(update, context, 'пёсик', DOG_URL)

# Функция-обработчик команды /start для приветствия и отправки первого изображения
def wake_up(update, context):
    # Получение объекта чата
    chat = update.effective_chat
    # Получение имени пользователя
    name = update.message.chat.first_name
    # Создание клавиатуры с кнопками /newcat и /newdog
    button = ReplyKeyboardMarkup([['/newcat', '/newdog']], resize_keyboard=True)
    # Отправка приветственного сообщения с именем пользователя и клавиатурой
    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашел!',
        reply_markup=button
    )
    # Получение URL изображения кота (по умолчанию)
    image = get_new_image(CAT_URL)
    # Логирование события отправки изображения
    logging.info(f'Отправлен котик {image} для {name}')
    # Отправка изображения в чат
    context.bot.send_photo(chat.id, image)

# Основная функция для запуска бота
def main():
    # Инициализация бота с использованием токена
    updater = Updater(token=secret_token)
    
    # Регистрация обработчиков команд /start, /newcat и /newdog
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('newdog', new_dog))
    
    # Запуск бота в режиме опроса новых сообщений
    updater.start_polling()
    # Ожидание завершения работы бота (например, при остановке программы)
    updater.idle()

# Запуск программы, если скрипт выполняется напрямую
if __name__ == '__main__':
    main()