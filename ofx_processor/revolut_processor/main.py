import csv
import os
from collections import defaultdict

import click
import dateparser

from ofx_processor.utils import ynab


def process_amount(amount):
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


def process_inflow(line):
    return process_amount(line.get("Paid In (EUR)"))


def process_outflow(line):
    return process_amount(line.get("Paid Out (EUR)"))


@click.command()
@click.argument("csv_filename")
@click.option(
    "--ynab/--no-ynab",
    "push_to_ynab",
    default=True,
    help="Push data directly to YNAB.",
    show_default=True,
)
@click.option(
    "--file/--no-file",
    "output_file",
    default=False,
    help="Write a processed file.",
    show_default=True,
)
def cli(csv_filename, push_to_ynab, output_file):
    formatted_data = []
    ynab_transactions = []
    transaction_ids = defaultdict(int)

    with open(csv_filename) as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            date = process_date(line)
            payee = line["Reference"]
            memo = process_memo(line)
            outflow = process_outflow(line)
            inflow = process_inflow(line)
            formatted_data.append(
                {
                    "Date": date,
                    "Payee": payee,
                    "Memo": memo,
                    "Outflow": outflow,
                    "Inflow": inflow,
                }
            )
            amount = outflow if outflow else inflow
            amount *= 1000
            import_id = f"YNAB:{amount}:{date}"
            transaction_ids[import_id] += 1
            occurrence = transaction_ids[import_id]
            import_id = f"{import_id}:{occurrence}"
            ynab_transactions.append(
                {
                    "date": date,
                    "amount": amount,
                    "payee_name": payee,
                    "memo": memo,
                    "import_id": import_id,
                }
            )

    if output_file and formatted_data:
        processed_file = os.path.join(os.path.dirname(csv_filename), "processed.csv")
        with open(processed_file, "w") as f:
            writer = csv.DictWriter(
                f, delimiter=",", quotechar='"', fieldnames=formatted_data[0].keys()
            )
            writer.writeheader()
            writer.writerows(formatted_data)

            click.secho("{} written".format(processed_file), fg="green")
    else:
        click.secho("Nothing to write.")

    if push_to_ynab and ynab_transactions:
        ynab.push_transactions(ynab_transactions, "revolut")


if __name__ == "__main__":
    cli()
