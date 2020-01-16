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
        filter(None, map(str.strip, [line["Category"], line["Exchange Rate"]]))
    )


@click.command()
@click.argument("csv_filename")
def cli(csv_filename):
    formatted_data = []

    with open(csv_filename) as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            date = dateparser.parse(line["Completed Date"])
            formatted_data.append(
                {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Payee": line["Reference"],
                    "Memo": process_memo(line),
                    "Outflow": process_amount(line["Paid Out (EUR)"]),
                    "Inflow": process_amount(line["Paid In (EUR)"]),
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
