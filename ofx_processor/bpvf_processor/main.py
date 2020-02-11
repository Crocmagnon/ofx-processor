import os
import re
import sys
from collections import defaultdict
from xml.etree import ElementTree

import click
from ofxtools.Parser import OFXTree
from ofxtools.header import make_header

from ofx_processor.utils import ynab


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

        return res_name, res_memo, True

    return name, memo, False


def process_name_and_memo(transaction):
    return _process_name_and_memo(transaction.name, transaction.memo)


@click.command()
@click.argument("ofx_filename")
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
def cli(ofx_filename, push_to_ynab, output_file):
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
        transaction.name, transaction.memo, edited = process_name_and_memo(transaction)

        if edited:
            click.secho(
                "Edited transaction {} ({})".format(
                    transaction.checknum, transaction.name
                ),
                fg="blue",
            )

        date = transaction.dtposted.isoformat().split("T")[0]
        amount = int(transaction.trnamt * 1000)
        import_id = f"YNAB:{amount}:{date}"
        transaction_ids[import_id] += 1
        occurrence = transaction_ids[import_id]
        import_id = f"{import_id}:{occurrence}"

        ynab_transactions.append(
            {
                "date": date,
                "amount": amount,
                "payee_name": transaction.name,
                "memo": transaction.memo,
                "import_id": import_id,
            }
        )
    click.secho(f"Processed {len(ynab_transactions)} transactions total.", fg="blue")

    if output_file:
        header = str(make_header(version=102))
        root = ofx.to_etree()
        data = ElementTree.tostring(root).decode()
        processed_file = os.path.join(os.path.dirname(ofx_filename), "processed.ofx")
        with open(processed_file, "w") as f:
            f.write(header + data)
            click.secho("{} written".format(processed_file), fg="green")

    if push_to_ynab and ynab_transactions:
        ynab.push_transactions(ynab_transactions, "bpvf")


if __name__ == "__main__":
    cli()
