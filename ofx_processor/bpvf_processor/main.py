import sys

import click
from ofxtools.Parser import OFXTree

from ofx_processor.bpvf_processor.bpvf_processor import BpvfProcessor
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

    processor = BpvfProcessor(ofx.statements[0].transactions)
    ynab_transactions = processor.get_transactions()

    click.secho(f"Processed {len(ynab_transactions)} transactions total.", fg="blue")

    ynab.push_transactions(ynab_transactions, "bpvf")
