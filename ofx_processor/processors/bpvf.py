import re

from ofx_processor.utils.base_ofx import OfxBaseLine, OfxBaseProcessor


class BpvfLine(OfxBaseLine):
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


class BpvfProcessor(OfxBaseProcessor):
    line_class = BpvfLine
    account_name = "bpvf"
    command_name = "bpvf"


def main(filename, keep, send_method):
    """Import BPVF bank statement (OFX file)."""
    processor = BpvfProcessor(filename)
    if send_method:
        processor.send_reconciled_amount(send_method)
    processor.push_to_ynab(keep)
