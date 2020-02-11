import configparser
import os

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

    return default_config


def push_transactions(transactions, account):
    config = configparser.ConfigParser()
    config_file = os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILENAME)
    if not os.path.isfile(config_file):
        os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)
        config = get_default_config()
        with open(config_file, "w") as file_:
            config.write(file_)
        click.secho("Editing config file...")
        click.pause()
        click.edit(filename=config_file)

    config.read(config_file)
    section = config[account]
    budget_id = section["budget"]
    url = f"{BASE_URL}/budgets/{budget_id}/transactions"
    for transaction in transactions:
        transaction["account_id"] = section["account"]

    data = {"transactions": transactions}
    token = section["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()
    data = res.json()["data"]

    created = set()
    for transaction in data["transactions"]:
        matched_id = transaction["matched_transaction_id"]
        if not matched_id or matched_id not in created:
            created.add(transaction["id"])
    click.secho(f"{len(created)} transactions created in YNAB.", fg="green", bold=True)

    duplicates = data["duplicate_import_ids"]
    if duplicates:
        click.secho(
            f"{len(duplicates)} transactions ignored (duplicates).", fg="yellow"
        )
