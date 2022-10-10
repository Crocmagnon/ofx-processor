import asyncio
import configparser
import os
import sys
from dataclasses import dataclass
from typing import Optional

import click
import telegram

DEFAULT_CONFIG_DIR = click.get_app_dir("ofx_processor")
DEFAULT_CONFIG_FILENAME = "config.ini"


def get_default_config():
    default_config = configparser.ConfigParser()
    default_config["DEFAULT"] = {
        "token": "<YOUR API TOKEN>",
        "budget": "<YOUR BUDGET ID>",
        "mailgun_api_key": "",
        "mailgun_domain": "",
        "mailgun_from": "",
        "email_recipient": "",
    }
    default_config["bpvf"] = {"account": "<YOUR ACCOUNT ID>"}
    default_config["revolut"] = {"account": "<YOUR ACCOUNT ID>"}
    default_config["ce"] = {"account": "<YOUR ACCOUNT ID>"}
    default_config["lcl"] = {
        "account": "<YOUR ACCOUNT ID>",
        "bank_identifier": "login",
        "bank_password": "password",
    }

    return default_config


def get_config_file_name():
    config_file = os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILENAME)
    return config_file


@click.group()
def config():
    """Manage configuration."""


@config.command("edit", help="Edit the config file.")
def edit_config():
    config_file = get_config_file_name()
    click.edit(filename=config_file)


@config.command("file", help="Print the config file path.")
def show_file_name():
    config_file = get_config_file_name()
    click.echo(config_file)


@config.command("telegram", help="Display the bot's chat ID.")
def print_telegram_chat_id():
    config = get_config("DEFAULT")
    click.pause("Please start a conversation with your bot, then press any key...")
    asyncio.run(print_chat_id(config))


async def print_chat_id(config: "Config"):
    bot = telegram.Bot(config.telegram_bot_token)
    async with bot:
        update = (await bot.get_updates())[-1]
        chat_id = update.message.chat_id
        click.secho(f"Your chat ID is: {chat_id}", fg="green", bold=True)


@dataclass(frozen=True)
class Config:
    account: str
    budget_id: str
    token: str
    bank_identifier: Optional[str] = None
    bank_password: Optional[str] = None
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    mailgun_from: Optional[str] = None
    email_recipient: Optional[str] = None
    sms_user: Optional[str] = None
    sms_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_bot_chat_id: Optional[str] = None
    home_assistant_webhook_url: Optional[str] = None

    @property
    def email_setup(self) -> bool:
        """Return true if all fields are setup for email."""
        return all(
            [
                self.mailgun_from,
                self.mailgun_domain,
                self.mailgun_api_key,
                self.email_recipient,
            ]
        )

    @property
    def sms_setup(self) -> bool:
        """Return true if all fields are setup for sms."""
        return all(
            [
                self.sms_user,
                self.sms_key,
            ]
        )

    @property
    def telegram_setup(self) -> bool:
        """Return true if all fields are setup for telegram."""
        return all(
            [
                self.telegram_bot_token,
                self.telegram_bot_chat_id,
            ]
        )

    @property
    def home_assistant_setup(self):
        """Return true if all fields are setup for home assistant."""
        return all(
            [
                self.home_assistant_webhook_url,
            ]
        )


def get_config(account: str) -> Config:
    config = configparser.ConfigParser()
    config_file = get_config_file_name()

    if not os.path.isfile(config_file):
        os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)
        config = get_default_config()
        with open(config_file, "w") as file_:
            config.write(file_)
        click.secho("Editing config file...")
        click.pause()
        click.edit(filename=config_file)

    try:
        config.read(config_file)
    except configparser.Error as e:
        return handle_config_file_error(config_file, e)

    try:
        section = config[account]
        budget_id = section["budget"]
        token = section["token"]
        if account == "DEFAULT":
            ynab_account_id = ""
        else:
            ynab_account_id = section["account"]
        bank_identifier = section.get("bank_identifier")
        bank_password = section.get("bank_password")
        mailgun_api_key = section.get("mailgun_api_key")
        mailgun_domain = section.get("mailgun_domain")
        mailgun_from = section.get("mailgun_from")
        email_recipient = section.get("email_recipient")
        sms_user = section.get("sms_user")
        sms_key = section.get("sms_key")
        telegram_bot_token = section.get("telegram_bot_token")
        telegram_bot_chat_id = section.get("telegram_bot_chat_id")
        home_assistant_webhook_url = section.get("home_assistant_webhook_url")
    except KeyError as e:
        return handle_config_file_error(config_file, e)

    return Config(
        ynab_account_id,
        budget_id,
        token,
        bank_identifier,
        bank_password,
        mailgun_api_key,
        mailgun_domain,
        mailgun_from,
        email_recipient,
        sms_user,
        sms_key,
        telegram_bot_token,
        telegram_bot_chat_id,
        home_assistant_webhook_url,
    )


def handle_config_file_error(config_file, e):
    click.secho(f"Error while parsing config file: {str(e)}", fg="red", bold=True)
    click.secho("Opening the file...")
    click.pause()
    click.edit(filename=config_file)
    click.secho("Exiting...", fg="red", bold=True)
    sys.exit(1)
