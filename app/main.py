from app.my_app import MyApp
from dotenv import load_dotenv
from os import getenv
import asyncio
import logging
import sys
from app.constants import Environment as Env


async def main() -> None:
    load_dotenv()
    tg_token = getenv(Env.Value.telegram_token)
    my_app = MyApp(tg_token)

    await my_app.dp.start_polling(my_app.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
