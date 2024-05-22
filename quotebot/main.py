import argparse
import asyncio
from collections.abc import Iterable, Sequence
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Callable, TypedDict, cast

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.inline_query import InlineQuery
from aiogram.types.inline_query_result_audio import InlineQueryResultAudio
from aiogram.utils.markdown import bold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from .config import Config

LOGGER = logging.getLogger("application")
CONFIG = Config()


class QuoteInfo(TypedDict):
    hero: str
    url: str
    lang: str
    lyrics: str


def read_quotes_file(file_path: str) -> list[QuoteInfo]:
    with open(file_path, "r", encoding="utf-8") as file:
        data: list[QuoteInfo] = json.load(file)
    return data


def validate_file_arg(arg_name: str) -> Callable[[str], Path]:
    def valid_file(path_str: str) -> Path:
        if not path_str:
            raise argparse.ArgumentTypeError(f"{arg_name} path not specified")
        path = Path(path_str)
        if not path.exists():
            raise argparse.ArgumentTypeError(f'The file "{path}" does not exist.')
        return path

    return valid_file


def init_handlers(dp: Dispatcher, bot: Bot, args: argparse.Namespace) -> None:
    quotes_data: list[QuoteInfo] = read_quotes_file(args.quotes_file)

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        user_name = getattr(message.from_user, "full_name", "noname")
        greetings = f"Hello, {bold(user_name)}"

        await message.answer(greetings)

    @dp.message()
    async def message_handler(message: Message) -> None:
        if not CONFIG.admin_ids:
            return
        for admin_id in CONFIG.admin_ids:
            await message.forward(chat_id=admin_id)

    @dp.inline_query()
    async def inline_query(message: InlineQuery) -> None:
        user_name = getattr(message.from_user, "full_name", "noname")
        LOGGER.debug(f"Inline from: {user_name}")

        results: list[InlineQueryResultAudio] = []
        for q in quotes_data:
            if len(results) >= 50:
                break
            if (
                message.query.lower() in q["hero"].lower()
                or message.query.lower() in q["lyrics"].lower()
            ):
                results.append(
                    InlineQueryResultAudio(
                        id=str(uuid.uuid4()),
                        audio_url=q["url"],
                        title=q["lyrics"],
                        performer=q["hero"],
                    )
                )
        await message.answer(list(results[:50]))

    # TODO: save user choose
    # @dp.chosen_inline_result()
    # async def chosen_inline_result(chosen_inline_result: types.ChosenInlineResult):
    #    pass


async def on_startup(bot: Bot) -> None:
    LOGGER.info(f"Registering webhook: {CONFIG.webhook_url}")
    await bot.set_webhook(f"{CONFIG.webhook_url}")


def main(bot: Bot, args: argparse.Namespace) -> None:
    dp = Dispatcher()
    init_handlers(dp, bot, args)
    dp.startup.register(on_startup)  # register webhook
    dp.shutdown.register(bot.delete_webhook)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    # Register webhook handler on application
    if not CONFIG.webhook_path:
        raise RuntimeError("webhook_path must be specified")
    webhook_requests_handler.register(app, path=CONFIG.webhook_path)
    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=CONFIG.backend_host, port=CONFIG.backend_port)


async def polling(bot: Bot, args: argparse.Namespace) -> None:
    dp = Dispatcher()
    init_handlers(dp, bot, args)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--polling", action="store_true", help="Enable polling mode.")

    parser.add_argument(
        "quotes_file",
        type=validate_file_arg("quotes_file"),
        help="Path to the JSON file with quotes.",
    )

    args: argparse.Namespace = parser.parse_args()

    bot = Bot(CONFIG.bot_token, default=DefaultBotProperties(parse_mode="MarkdownV2"))

    if args.polling:
        asyncio.run(polling(bot, args))
    else:
        main(bot, args)
