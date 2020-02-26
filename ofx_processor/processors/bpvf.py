import re
import sys

import click
from ofxtools import OFXTree
from ofxtools.header import OFXHeaderError

from ofx_processor.utils.processor import Processor, Line


class BpvfLine(Line):
    def __init__(self, data=None):
        super(BpvfLine, self).__init__(data)

    def get_date(self):
        return self.data.dtposted.isoformat().split("T")[0]

    def get_amount(self):
        return int(self.data.trnamt * 1000)

    def get_memo(self):
        return self._process_name_and_memo(self.data.name, self.data.memo)[1]

    def get_payee(self):
        return self._process_name_and_memo(self.data.name, self.data.memo)[0]

    @staticmethod
    def _process_name_and_memo(name: str, memo: str):
        if "CB****" in name:
            conversion = re.compile(r"\d+,\d{2}[a-zA-Z]{3}")
            match = conversion.search(memo)
            if match:
                res_name = memo[: match.start() - 1]
                res_memo = name + memo[match.start() - 1 :]
            else:
                res_name = memo
                res_memo = name

            return res_name, res_memo

        return name, memo


class BpvfProcessor(Processor):
    line_class = BpvfLine
    account_name = "bpvf"

    def parse_file(self):
        parser = OFXTree()
        try:
            parser.parse(self.filename)
        except (FileNotFoundError, OFXHeaderError):
            click.secho("Couldn't open or parse ofx file", fg="red")
            sys.exit(1)

        ofx = parser.convert()

        if ofx is None:
            click.secho("Couldn't convert ofx file", fg="red")
            sys.exit(1)

        return ofx.statements[0].transactions

    @staticmethod
    @click.command("bpvf", help="Process BPVF bank statement (OFX)")
    @click.argument("ofx_filename")
    def main(ofx_filename):
        BpvfProcessor(ofx_filename).push_to_ynab()
