import asyncio

from aiohttp import web

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import config
import create_mp3
from config import MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET, MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET
import db
import snippets

# Создание экземпляра бота и диспетчера
bot = Bot(config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# SCOPIROVANNIY COD IZ AIOGRAM_3.x DOKI
WEB_SERVER_HOST = "194.58.109.189"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8080

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = config.BOT_TOKEN
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = "https://aiogram.dev/"


router = Router()

path_to_db = "Music_db.db"
path_to_snippets_json = "snippets.json"
path_to_music = "music/"
path_to_snippets_dict = "snippets/"


def snippets_work(answer_db: list[tuple]) -> tuple:
    track_id = answer_db[0][0]
    snippet_list = snippets.get_snippet_list(track_id, path_to_snippets_json=path_to_snippets_json)
    zone = snippets.create_seconds_zone(snippet_list, MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET=MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET,
                                        MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET=MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET)
    return zone


@router.message(CommandStart())
async def start_command(message: types.Message) -> None:
    # Отправляем приветственное сообщение пользователю
    await message.answer("Привет!")


# @router.message(Command('stats'))
# async def stats_command(message: types.Message) -> None:
#     try:
#         key = message.text.split()[1]
#     except IndexError:
#         key = "жанр"
#     await message.answer("Статистика" + key)


@router.message(Command('help'))
async def help_command(message: types.Message) -> None:
    await message.answer(
        "Помощь:\nЧтобы получить сниппет просто введите название трека\nЧтобы помсотреть статистику по трекам введите "
        "команду: /stats")


# Создание функции-обработчика текстовых сообщений
@router.message()
async def handle_text(message: types.Message):
    search_text = message.text
    # Ваш код для обработки текстового сообщения

    answer = str()

    answer_db = db.search(search_text=search_text, path_to_db=path_to_db)

    if len(answer_db) == 0:
        answer = f"Ничего не найдено по запросу: {search_text}"
        await message.answer(answer)
    elif len(answer_db) == 1:
        title = answer_db[0][1]
        answer = f"Найден один трек: {title}"
        await message.answer(answer)

        zone = snippets_work(answer_db)

        track_id = answer_db[0][0]

        if zone:

            create_mp3.create(path_to_music + str(track_id) + ".mp3", zone[0], zone[1], path_to_snippets_dict)

            with open(path_to_snippets_dict + f"snippet_{track_id}.mp3", "rb") as f:
                await message.answer_audio(f)

        else:
            await message.answer("Сниппет не готов")
    elif len(answer_db) > 10:
        answer = "Найдено больше 10 треков. Дополните запрос"
        await message.answer(answer)
    else:
        count = 1
        for track in answer_db:
            answer += f"{count}. {track[1]}\n"
            count += 1
        await message.answer(answer + "\nНапишите полное название трека")



async def main() -> None:
    dp.include_routers(
        router,
    )

    await bot.delete_webhook(drop_pending_updates=True)

    # app = web.Application()

    # webhook_requests_handler = SimpleRequestHandler(
        # dispatcher=dp,
        # bot=bot,
        # secret_token=WEBHOOK_SECRET,
    # )

    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # setup_application(app, dp, bot=bot)

    # web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    await dp.start_polling(bot)

asyncio.run(main())
# Запуск бота
# if __name__ == '__main__':
    # asyncio.run(main())

