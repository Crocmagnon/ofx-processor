from decimal import Decimal

import click
import requests

from ofx_processor.utils.config import Config


def send(config: Config, amount: Decimal) -> None:
    if not config.home_assistant_setup:
        click.secho("Home Assistant is not properly setup", fg="yellow")
        return
    res = requests.post(
        config.home_assistant_webhook_url,
        json={
            "reconciled": str(amount),
        },
    )
    if res.status_code >= 400:
        click.secho("Error while calling Home Assistant", fg="yellow")
