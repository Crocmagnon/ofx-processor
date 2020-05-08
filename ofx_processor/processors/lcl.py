import sys

import click

from ofx_processor.utils.base_ofx import OfxBaseLine, OfxBaseProcessor


class LclLine(OfxBaseLine):
    pass


class LclProcessor(OfxBaseProcessor):
    line_class = LclLine
    account_name = "lcl"
    command_name = "lcl"

    def parse_file(self):
        # The first line of this file needs to be removed.
        # It contains something that is not part of the header of an OFX file.
        try:
            with open(self.filename, "r") as user_file:
                data = user_file.read().splitlines(True)
        except FileNotFoundError:
            click.secho("Couldn't find ofx file", fg="red")
            sys.exit(1)

        if "Content-Type:" in data[0]:
            with open(self.filename, "w") as temp_file:
                temp_file.writelines(data[1:])

        transactions = super(LclProcessor, self).parse_file()

        if "Content-Type:" in data[0]:
            with open(self.filename, "w") as temp_file:
                temp_file.writelines(data)

        return transactions


def main(filename, keep):
    """Import LCL bank statement (OFX file)."""
    LclProcessor(filename).push_to_ynab(keep)
