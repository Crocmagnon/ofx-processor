from decimal import Decimal

import click
import requests

from ofx_processor.utils.config import Config


def send(config: Config, amount: Decimal) -> None:
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
