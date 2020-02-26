import re

import click

from ofx_processor.processors.bpvf import BpvfProcessor, BpvfLine


class CeLine(BpvfLine):
    @staticmethod
    def _process_name_and_memo(name: str, memo: str):
        name = name.strip()
        cb_format = re.compile(r"FACT \d{6}$")
        match = cb_format.search(name)
        if match:
            res_name = name[: match.start() - 1].strip()
            res_memo = name[match.start() - 1 :].strip()
        else:
            res_name = name
            res_memo = memo
        return res_name, res_memo


class CeProcessor(BpvfProcessor):
    account_name = "ce"
    line_class = CeLine

    @staticmethod
    @click.command("ce", help="Process CE bank statement (OFX)")
    @click.argument("ofx_filename")
    def main(ofx_filename):
        CeProcessor(ofx_filename).push_to_ynab()
