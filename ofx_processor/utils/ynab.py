import configparser
import os
import sys

import click
import requests

BASE_URL = "https://api.youneedabudget.com/v1"
DEFAULT_CONFIG_DIR = click.get_app_dir("ofx_processor")
DEFAULT_CONFIG_FILENAME = "config.ini"


def get_default_config():
    default_config = configparser.ConfigParser()
    default_config["DEFAULT"] = {
        "token": "<YOUR API TOKEN>",
        "budget": "<YOUR BUDGET ID>",
    }
    default_config["bpvf"] = {"account": "<YOUR ACCOUNT ID>"}
    default_config["revolut"] = {"account": "<YOUR ACCOUNT ID>"}
    default_config["ce"] = {"account": "<YOUR ACCOUNT ID>"}

    return default_config


def get_config_file_name():
    config_file = os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILENAME)
    return config_file


@click.group()
def config():
    """Manage configuration."""


@config.command("edit")
def edit_config():
    config_file = get_config_file_name()
    click.edit(filename=config_file)


def push_transactions(transactions, account):
    if not transactions:
        click.secho("No transaction, nothing to do.", fg="yellow")
        return
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
        account = section["account"]
    except KeyError as e:
        return handle_config_file_error(config_file, e)

    url = f"{BASE_URL}/budgets/{budget_id}/transactions"
    for transaction in transactions:
        transaction["account_id"] = account
        transaction["cleared"] = "cleared"

    data = {"transactions": transactions}
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()
    data = res.json()["data"]

    created = set()
    for transaction in data["transactions"]:
        matched_id = transaction.get("matched_transaction_id")
        if not matched_id or matched_id not in created:
            created.add(transaction["id"])

    if created:
        click.secho(
            f"{len(created)} transactions created in YNAB.", fg="green", bold=True
        )

    duplicates = data["duplicate_import_ids"]
    if duplicates:
        click.secho(
            f"{len(duplicates)} transactions ignored (duplicates).", fg="yellow"
        )


def handle_config_file_error(config_file, e):
    click.secho(f"Error while parsing config file: {str(e)}", fg="red", bold=True)
    click.secho("Opening the file...")
    click.pause()
    click.edit(filename=config_file)
    click.secho("Exiting...", fg="red", bold=True)
    sys.exit(1)
