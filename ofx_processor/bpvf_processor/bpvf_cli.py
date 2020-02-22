import click

from ofx_processor.bpvf_processor.bpvf_processor import BpvfProcessor


@click.command(help="Process BPVF bank statement (OFX)")
@click.argument("ofx_filename")
def main(ofx_filename):
    BpvfProcessor(ofx_filename).push_to_ynab()
