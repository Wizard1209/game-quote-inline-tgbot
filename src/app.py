import asyncio
from pathlib import Path
import sys
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types.inline_query import InlineQuery
from aiogram.utils.markdown import bold
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


LOGGER = logging.getLogger('application')

WEBHOOK_PATH = '/bot'
WEBHOOK_URL = 'https://ltgmc.online/{WEBHOOK_PATH}'

BACKEND_HOST = '0.0.0.0'
BACKEND_PORT = 80


def load_api_key(api_key_path: Path):
    if not api_key_path.exists():
        raise FileNotFoundError('API key path does not exist')

    return api_key_path.read_text().strip()


def init_handlers(dp: Dispatcher, bot: Bot):
    @dp.message()
    async def command_start_handler(message: Message) -> None:
        LOGGER.debug(f'Message: {getattr(message.from_user, 'full_name', 'noname')} - {message.text or message.content_type if len(message.text or message.content_type) < 15 else 'Long message'}')
        await message.answer(f'Hello, {bold(getattr(message.from_user, "full_name", "noname"))}\\!')

    @dp.inline_query()
    async def inline_query(message: InlineQuery) -> None:
        LOGGER.debug(f'Inline: {message.from_user.full_name} - {message.query if len(message.query) < 15 else 'Long query'}')
        #await message.answer([r1, r2])


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f'{WEBHOOK_URL}')


def main(bot: Bot) -> None:
    dp = Dispatcher()
    init_handlers(dp, bot)
    dp.startup.register(on_startup) # register webhook

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
    # await dp.start_polling(bot)


if __name__ == '__main__':
    # TODO: debug log all loggers
    # TODO: write webhook
    # TODO: add flag for selecting polling or webhook
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    if len(sys.argv) < 2:
        raise RuntimeError('Path for API key was not provided')
    api_key = load_api_key(Path(sys.argv[1]))
    bot = Bot(api_key, default=DefaultBotProperties(parse_mode='MarkdownV2'))
    main(bot)
