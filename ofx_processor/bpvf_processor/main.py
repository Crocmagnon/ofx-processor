import re
import sys
from collections import defaultdict

import click
from ofxtools.Parser import OFXTree

from ofx_processor.utils import ynab


@click.command(help="Process BPVF bank statement (OFX)")
@click.argument("ofx_filename")
def cli(ofx_filename):
    parser = OFXTree()
    try:
        parser.parse(ofx_filename)
    except FileNotFoundError:
        click.secho("Couldn't open ofx file", fg="red")
        sys.exit(1)

    ofx = parser.convert()

    if ofx is None:
        click.secho("Couldn't parse ofx file", fg="red")
        sys.exit(1)

    ynab_transactions = []
    transaction_ids = defaultdict(int)

    for transaction in ofx.statements[0].transactions:
        ynab_transaction = line_to_ynab_transaction(transaction, transaction_ids)
        ynab_transactions.append(ynab_transaction)
    click.secho(f"Processed {len(ynab_transactions)} transactions total.", fg="blue")

    ynab.push_transactions(ynab_transactions, "bpvf")


def _process_name_and_memo(name, memo):
    if "CB****" in name:
        conversion = re.compile(r"\d+,\d{2}[a-zA-Z]{3}")
        match = conversion.search(memo)
        if match:
            res_name = memo[: match.start() - 1]
            res_memo = name + memo[match.start() - 1 :]
        else:
            res_name = memo
            res_memo = name

        return res_name, res_memo

    return name, memo


def process_payee(line):
    return _process_name_and_memo(line.name, line.memo)[0]


def process_memo(line):
    return _process_name_and_memo(line.name, line.memo)[1]


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


def process_date(transaction):
    return transaction.dtposted.isoformat().split("T")[0]


def process_amount(transaction):
    return int(transaction.trnamt * 1000)


if __name__ == "__main__":
    cli()
