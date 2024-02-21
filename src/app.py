import asyncio
from pathlib import Path
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import bold

def load_api_key(api_key_path: Path):
    if not api_key_path.exists():
        raise FileNotFoundError("API key path does not exist")

    return api_key_path.read_text()


def init_handlers(dp: Dispatcher):
    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        await message.answer(f"Hello, {bold(getattr(message.from_user, 'full_name', 'noname'))}!")


async def main(bot: Bot) -> None:
    dp = Dispatcher()
    init_handlers(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError("Path for API key was not provided")
    api_key = load_api_key(Path(sys.argv[1]))
    bot = Bot(api_key)
    asyncio.run(main(bot))
