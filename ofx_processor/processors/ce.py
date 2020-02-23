import click

from ofx_processor.processors.bpvf import BpvfProcessor


class CeProcessor(BpvfProcessor):
    account_name = "ce"

    @staticmethod
    @click.command("ce", help="Process CE bank statement (OFX)")
    @click.argument("ofx_filename")
    def main(ofx_filename):
        CeProcessor(ofx_filename).push_to_ynab()
