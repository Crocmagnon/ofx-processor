import click

from ofx_processor.ce_processor.ce_processor import CeProcessor


@click.command(help="Process CE bank statement (OFX)")
@click.argument("ofx_filename")
def main(ofx_filename):
    CeProcessor(ofx_filename).push_to_ynab()
