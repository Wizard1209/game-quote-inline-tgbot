import argparse
import asyncio
import json
from pathlib import Path
import sys
import logging
from typing import Callable, TypedDict
import uuid

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_audio import InlineQueryResultAudio
from aiogram.utils.markdown import bold
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


LOGGER = logging.getLogger('application')

WEBHOOK_PATH = '/bot'
WEBHOOK_URL = f'https://ltgmc.online{WEBHOOK_PATH}'

BACKEND_HOST = '0.0.0.0'
BACKEND_PORT = 80


class QuoteInfo(TypedDict):
    hero: str
    url: str
    lang: str
    lyrics: str


def read_quotes_file(file_path: str) -> list[QuoteInfo]:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def validate_file_arg(arg_name: str) -> Callable[[str], Path]:
    def valid_file(path_str: str) -> Path:
        if not path_str:
            raise argparse.ArgumentTypeError(f'{arg_name} path not specified')
        path = Path(path_str)
        if not path.exists():
            raise argparse.ArgumentTypeError(f'The file "{path}" does not exist.')
        return path
    
    return valid_file


def load_api_key(api_key_path: Path):
    return api_key_path.read_text().strip()


def init_handlers(dp: Dispatcher, bot: Bot, args: argparse.Namespace):
    quotes_data: list[QuoteInfo] = read_quotes_file(args.quotes_file)

    @dp.message()
    async def command_start_handler(message: Message) -> None:
        LOGGER.debug(f'Message: {getattr(message.from_user, 'full_name', 'noname')} - {message.text or message.content_type if len(message.text or message.content_type) < 15 else 'Long message'}')
        await message.answer(f'Hello, {bold(getattr(message.from_user, "full_name", "noname"))}\\!')

    @dp.inline_query()
    async def inline_query(message: InlineQuery) -> None:
        LOGGER.debug(f'Inline: {message.from_user.full_name} - {message.query if len(message.query) < 15 else 'Long query'}')
        results: list[InlineQueryResultAudio] = []
        for q in quotes_data:
            if message.query.lower() in q['hero'].lower() or message.query.lower() in q['lyrics'].lower():
                results.append(InlineQueryResultAudio(
                    id=str(uuid.uuid4()),
                    audio_url=q['url'],
                    title=q['lyrics'],
                    performer=q['hero']
                ))
        await message.answer(list(results))  # TODO: fix mypy xd no comments)

    # TODO: save user choose
    #@dp.chosen_inline_result()
    #async def chosen_inline_result(chosen_inline_result: types.ChosenInlineResult):
    #    pass


async def on_startup(bot: Bot) -> None:
    LOGGER.info(f'Registering webhook: {WEBHOOK_URL}')
    await bot.set_webhook(f'{WEBHOOK_URL}')


def main(bot: Bot, args: argparse.Namespace) -> None:
    dp = Dispatcher()
    init_handlers(dp, bot, args)
    dp.startup.register(on_startup) # register webhook
    # TODO: delete webhook on shutdown

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=BACKEND_HOST, port=BACKEND_PORT)


async def polling(bot: Bot, args: argparse.Namespace):
    dp = Dispatcher()
    init_handlers(dp, bot, args)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--polling', action='store_true', help='Enable polling mode.')
    parser.add_argument('api_key', type=validate_file_arg('api_key'), help='Path to the API key file.')
    parser.add_argument('quotes_file', type=validate_file_arg('quotes_file'), help='Path to the JSON file with quotes.')

    args: argparse.Namespace = parser.parse_args()

    api_key = load_api_key(args.api_key)

    bot = Bot(api_key, default=DefaultBotProperties(parse_mode='MarkdownV2'))
    
    if args.polling:
        asyncio.run(polling(bot, args))
    else:
        main(bot, args)
