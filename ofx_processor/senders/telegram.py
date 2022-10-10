import asyncio
from decimal import Decimal

import click
import telegram

from ofx_processor.utils.config import Config


def send(config: Config, amount: Decimal) -> None:
    if not config.telegram_setup:
        click.secho("Telegram is not properly setup", fg="yellow")
        return

    try:
        asyncio.run(_send_telegram_message(config.telegram_bot_token, config.telegram_bot_chat_id, f"Reconciled balance: {amount}"))
    except Exception as e:
        click.secho(f"Error while sending Telegram message. {type(e).__name__}: {e}", fg="yellow")


async def _send_telegram_message(bot_token: str, chat_id: str, message: str) -> None:
    bot = telegram.Bot(bot_token)
    async with bot:
        await bot.send_message(chat_id=chat_id, text=message)
