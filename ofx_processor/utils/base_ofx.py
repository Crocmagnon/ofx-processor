import sys
from decimal import Decimal

import click
from ofxtools import OFXTree
from ofxtools.header import OFXHeaderError
from ofxtools.models import Aggregate

from ofx_processor.senders import SENDERS
from ofx_processor.utils.base_processor import BaseLine, BaseProcessor
from ofx_processor.utils.config import get_config


class OfxBaseLine(BaseLine):
    def get_date(self):
        return self.data.dtposted.isoformat().split("T")[0]

    def get_amount(self):
        return int(self.data.trnamt * 1000)

    def get_memo(self):
        return self.data.memo

    def get_payee(self):
        return self.data.name


class OfxBaseProcessor(BaseProcessor):
    line_class = OfxBaseLine
    account_name = ""

    def parse_file(self):
        ofx = self._parse_file()
        return ofx.statements[0].transactions

    def send_reconciled_amount(self, method):
        amount = self._get_reconciled_amount()
        click.secho(f"Reconciled balance: {amount}. Sending via {method}...", fg="blue")
        config = get_config(self.account_name)
        sender = SENDERS.get(method)
        if sender:
            sender(config, amount)
        else:
            click.secho(f"Method not implemented: {method}.", fg="red", bold=True)

    def _get_reconciled_amount(self) -> Decimal:
        ofx = self._parse_file()
        return ofx.statements[0].balance.balamt

    def _parse_file(self) -> Aggregate:
        parser = OFXTree()
        try:
            parser.parse(self.filename)
        except (FileNotFoundError, OFXHeaderError):
            click.secho("Couldn't open or parse ofx file", fg="red")
            sys.exit(1)
        ofx = parser.convert()
        return ofx

