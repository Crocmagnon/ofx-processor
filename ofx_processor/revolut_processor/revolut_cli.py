import click

from ofx_processor.revolut_processor.revolut_processor import RevolutProcessor


@click.command(help="Process Revolut bank statement (CSV)")
@click.argument("csv_filename")
def main(csv_filename):
    RevolutProcessor(csv_filename).push_to_ynab()
