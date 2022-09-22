import asyncio
import sys
from decimal import Decimal

import click
import requests
import telegram
from ofxtools import OFXTree
from ofxtools.header import OFXHeaderError
from ofxtools.models import Aggregate

from ofx_processor.utils.base_processor import BaseLine, BaseProcessor
from ofx_processor.utils.config import get_config


class OfxBaseLine(BaseLine):
    def get_date(self):
        return self.data.dtposted.isoformat().split("T")[0]

    def get_amount(self):
        return int(self.data.trnamt * 1000)

    def get_memo(self):
        return self.data.memo

    def get_payee(self):
        return self.data.name


class OfxBaseProcessor(BaseProcessor):
    line_class = OfxBaseLine
    account_name = ""

    def parse_file(self):
        ofx = self._parse_file()
        return ofx.statements[0].transactions

    def send_reconciled_amount(self, method):
        amount = self._get_reconciled_amount()
        click.secho(f"Reconciled balance: {amount}. Sending via {method}...", fg="blue")
        if method == "email":
            self._send_mail(amount)
        elif method == "sms":
            self._send_sms(amount)
        elif method == "telegram":
            self._send_telegram(amount)

    def _get_reconciled_amount(self) -> Decimal:
        ofx = self._parse_file()
        return ofx.statements[0].balance.balamt

    def _parse_file(self) -> Aggregate:
        parser = OFXTree()
        try:
            parser.parse(self.filename)
        except (FileNotFoundError, OFXHeaderError):
            click.secho("Couldn't open or parse ofx file", fg="red")
            sys.exit(1)
        ofx = parser.convert()
        return ofx

    def _send_mail(self, amount: Decimal):
        config = get_config(self.account_name)
        if not config.email_setup:
            click.secho("Email is not properly setup", fg="yellow")
            return
        res = requests.post(
            f"https://api.mailgun.net/v3/{config.mailgun_domain}/messages",
            auth=("api", config.mailgun_api_key),
            data={
                "from": config.mailgun_from,
                "to": [config.email_recipient],
                "subject": f"Reconciled balance: {amount}",
                "text": f"Here's your reconciled balance: {amount}",
            },
        )
        if res.status_code >= 400:
            click.secho("Error while sending email", fg="yellow")

    def _send_sms(self, amount: Decimal):
        config = get_config(self.account_name)
        if not config.sms_setup:
            click.secho("SMS is not properly setup", fg="yellow")
            return
        res = requests.post(
            f"https://smsapi.free-mobile.fr/sendmsg",
            json={
                "user": config.sms_user,
                "pass": config.sms_key,
                "msg": f"Reconciled balance: {amount}",
            },
        )
        if res.status_code >= 400:
            click.secho("Error while sending SMS", fg="yellow")

    def _send_telegram(self, amount: Decimal):
        config = get_config(self.account_name)
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
