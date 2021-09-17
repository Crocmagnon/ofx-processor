import csv
import re
import sys

import click
import dateparser

from ofx_processor.utils.base_processor import BaseProcessor, BaseLine


def _amount_str_to_float(amount: str):
    if amount:
        amount = amount.replace(",", ".")
        amount = re.sub(r"\s+", "", amount)
        return float(amount)
    return ""


class RevolutLine(BaseLine):
    def _process_inflow(self):
        return _amount_str_to_float(self.data.get("Paid In (EUR)"))

    def _process_outflow(self):
        return _amount_str_to_float(self.data.get("Paid Out (EUR)"))

    def get_date(self):
        return dateparser.parse(self.data.get("Completed Date")).strftime("%Y-%m-%d")

    def get_amount(self):
        outflow = self._process_outflow()
        inflow = self._process_inflow()
        amount = -outflow if outflow else inflow
        amount = int(amount * 1000)
        return amount

    def get_memo(self):
        return " - ".join(
            filter(
                None,
                map(
                    str.strip,
                    [self.data.get("Category", ""), self.data.get("Exchange Rate", "")],
                ),
            )
        )

    def get_payee(self):
        return self.data.get("Reference")


class RevolutProcessor(BaseProcessor):
    line_class = RevolutLine
    account_name = "revolut"
    command_name = "revolut"

    def parse_file(self):
        try:
            with open(self.filename, encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=";")
                return [line for line in reader]
        except FileNotFoundError:
            click.secho("File not found", fg="red")
            sys.exit(1)


def main(filename, keep):
    """Import Revolut bank statement (CSV file)."""
    RevolutProcessor(filename).push_to_ynab(keep)
