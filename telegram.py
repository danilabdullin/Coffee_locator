import sys
import os
import yaml
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from LLM_manager import LLMHandler


class TelegramBot:
    def __init__(self, config_path='config.yaml'):
        # Загрузка конфигурации из файла
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Инициализация Telegram Bot API
        telegram_token = os.getenv(config.get('telegram_api_token_name'))
        self.bot = Bot(telegram_token, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()

        # Инициализация обработчика для Language Model
        llm_api_key = os.getenv(config.get('openai_token_name'))
        model = config.get('LLM_version')
        self.llm_handler = LLMHandler(openai_api_key=llm_api_key, model=model)

        # Регистрация обработчиков сообщений
        self.register_handlers()

    def register_handlers(self):
        # Назначение функций-обработчиков для различных типов сообщений
        self.dp.message(CommandStart())(self.command_start_handler)
        self.dp.message()(self.echo_handler)

    async def command_start_handler(self, message: Message) -> None:
        # Обработчик команды /start
        await message.answer("Привет! Подскажи в каком городе ты находишься, и я подскажу лучшие кофейни там!")

    async def echo_handler(self, message: types.Message) -> None:
        # Обработчик для всех текстовых сообщений
        try:
            # Список фраз для случайного выбора
            phrases = [
                "Минутку...",
                "Запрос принят...",
                "Ожидайте...",
                "Обрабатываю ваш запрос...",
                "Секундочку, пожалуйста...",
                "Ваш запрос в обработке...",
                "Подождите немного...",
                "Занимаюсь вашим вопросом...",
                "Сейчас все будет...",
                "Работаю над этим...",
                "Принято к исполнению...",
                "Обработка запроса...",
                "Скоро узнаете ответ...",
                "Ваш запрос в приоритете...",
                "Уже почти готово..."
            ]

            # Выбор случайной фразы и отправка ее пользователю
            random_phrase = random.choice(phrases)
            await message.answer(random_phrase)

            # Обработка запроса пользователя и отправка ответа
            response = await self.llm_handler.get_response(user_id=message.from_user.id, context=message.text)
            await message.answer(response, parse_mode='Markdown')
        except Exception as e:
            # Обработка исключений
            await message.answer(f"Сори, Сори, что-то пошло не так, мы уже исправляем!")

    async def run(self):
        # Запуск бота
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Создание и запуск экземпляра бота
    telegram_bot = TelegramBot()
    asyncio.run(telegram_bot.run())
