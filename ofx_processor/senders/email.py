from decimal import Decimal

import click
import requests

from ofx_processor.utils.config import Config


def send(config: Config, amount: Decimal) -> None:
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
