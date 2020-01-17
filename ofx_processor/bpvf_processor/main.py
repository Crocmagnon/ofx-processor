import os
import re
import sys
from xml.etree import ElementTree

import click
from ofxtools.Parser import OFXTree
from ofxtools.header import make_header


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

    for transaction in ofx.statements[0].transactions:
        transaction.name, transaction.memo, edited = process_name_and_memo(transaction)

        if edited:
            click.secho(
                "Edited transaction {} ({})".format(
                    transaction.checknum, transaction.name
                ),
                fg="blue",
            )

    header = str(make_header(version=102))
    root = ofx.to_etree()
    data = ElementTree.tostring(root).decode()

    processed_file = os.path.join(os.path.dirname(ofx_filename), "processed.ofx")
    with open(processed_file, "w") as f:
        f.write(header + data)
        click.secho("{} written".format(processed_file), fg="green")


if __name__ == "__main__":
    cli()
