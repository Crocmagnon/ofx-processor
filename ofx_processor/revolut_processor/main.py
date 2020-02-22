import csv

import click

from ofx_processor.revolut_processor.revolut_processor import RevolutProcessor
from ofx_processor.utils import ynab


@click.command(help="Process Revolut bank statement (CSV)")
@click.argument("csv_filename")
def cli(csv_filename):
    with open(csv_filename) as f:
        reader = csv.DictReader(f, delimiter=";")
        processor = RevolutProcessor(reader)
        ynab_transactions = processor.get_transactions()

    click.secho(f"Processed {len(ynab_transactions)} transactions total.", fg="blue")
    ynab.push_transactions(ynab_transactions, "revolut")
