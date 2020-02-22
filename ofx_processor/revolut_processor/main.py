import csv
from collections import defaultdict

import click
import dateparser

from ofx_processor.utils import ynab


@click.command(help="Process Revolut bank statement (CSV)")
@click.argument("csv_filename")
def cli(csv_filename):
    ynab_transactions = []
    transaction_ids = defaultdict(int)

    with open(csv_filename) as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            ynab_transaction = line_to_ynab_transaction(line, transaction_ids)
            ynab_transactions.append(ynab_transaction)
    click.secho(f"Processed {len(ynab_transactions)} transactions total.", fg="blue")

    ynab.push_transactions(ynab_transactions, "revolut")


def _amount_str_to_float(amount):
    if amount:
        return float(amount.replace(",", "."))
    return ""


def process_memo(line):
    return " - ".join(
        filter(
            None,
            map(str.strip, [line.get("Category", ""), line.get("Exchange Rate", "")]),
        )
    )


def process_date(line):
    return dateparser.parse(line.get("Completed Date")).strftime("%Y-%m-%d")


def _process_inflow(line):
    return _amount_str_to_float(line.get("Paid In (EUR)"))


def _process_outflow(line):
    return _amount_str_to_float(line.get("Paid Out (EUR)"))


def process_amount(line):
    outflow = _process_outflow(line)
    inflow = _process_inflow(line)
    amount = -outflow if outflow else inflow
    amount = int(amount * 1000)
    return amount


def line_to_ynab_transaction(line, transaction_ids):
    date = process_date(line)
    payee = process_payee(line)
    memo = process_memo(line)
    amount = process_amount(line)
    import_id = f"YNAB:{amount}:{date}"
    transaction_ids[import_id] += 1
    occurrence = transaction_ids[import_id]
    import_id = f"{import_id}:{occurrence}"
    ynab_transaction = {
        "date": date,
        "amount": amount,
        "payee_name": payee,
        "memo": memo,
        "import_id": import_id,
    }
    return ynab_transaction


def process_payee(line):
    payee = line["Reference"]
    return payee
