import sys

import click
from ofxtools import OFXTree
from ofxtools.header import OFXHeaderError

from ofx_processor.utils.base_processor import BaseLine, BaseProcessor


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

    def parse_file(self):
        parser = OFXTree()
        try:
            parser.parse(self.filename)
        except (FileNotFoundError, OFXHeaderError):
            click.secho("Couldn't open or parse ofx file", fg="red")
            sys.exit(1)

        ofx = parser.convert()
        return ofx.statements[0].transactions
