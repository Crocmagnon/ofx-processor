import csv
import os

import click
import dateparser


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
def cli(csv_filename):
    formatted_data = []

    with open(csv_filename) as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            formatted_data.append(
                {
                    "Date": process_date(line),
                    "Payee": line["Reference"],
                    "Memo": process_memo(line),
                    "Outflow": process_outflow(line),
                    "Inflow": process_inflow(line),
                }
            )

    if not formatted_data:
        click.secho("Nothing to write.")

    processed_file = os.path.join(os.path.dirname(csv_filename), "processed.csv")
    with open(processed_file, "w") as f:
        writer = csv.DictWriter(
            f, delimiter=",", quotechar='"', fieldnames=formatted_data[0].keys()
        )
        writer.writeheader()
        writer.writerows(formatted_data)

        click.secho("{} written".format(processed_file), fg="green")


if __name__ == "__main__":
    cli()
