import csv

import click
import dateparser

from ofx_processor.utils.processor import Processor, Line


def _amount_str_to_float(amount):
    if amount:
        return float(amount.replace(",", "."))
    return ""


class RevolutLine(Line):
    def __init__(self, data: dict = None):
        super(RevolutLine, self).__init__(data)

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


class RevolutProcessor(Processor):
    line_class = RevolutLine
    account_name = "revolut"

    def parse_file(self):
        with open(self.filename) as f:
            reader = csv.DictReader(f, delimiter=";")
            return reader

    @staticmethod
    @click.command("revolut", help="Process Revolut bank statement (CSV)")
    @click.argument("csv_filename")
    def main(csv_filename):
        RevolutProcessor(csv_filename).push_to_ynab()
