import click
import requests

from ofx_processor.utils.config import get_config

BASE_URL = "https://api.youneedabudget.com/v1"


def push_transactions(transactions, account):
    if not transactions:
        click.secho("No transaction, nothing to do.", fg="yellow")
        return
    config = get_config(account)

    url = f"{BASE_URL}/budgets/{config.budget_id}/transactions"
    for transaction in transactions:
        transaction["account_id"] = config.account
        transaction["cleared"] = "cleared"

    data = {"transactions": transactions}
    headers = {"Authorization": f"Bearer {config.token}"}

    res = requests.post(url, json=data, headers=headers)
    if res.status_code >= 400:
        click.secho(f"Error pushing transactions: {res.text}", fg="red")
        return
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
