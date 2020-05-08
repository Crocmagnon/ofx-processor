import re

from ofx_processor.utils.base_ofx import OfxBaseProcessor, OfxBaseLine


class CeLine(OfxBaseLine):
    def get_memo(self):
        return self._process_name_and_memo(self.data.name, self.data.memo)[1]

    def get_payee(self):
        return self._process_name_and_memo(self.data.name, self.data.memo)[0]

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


class CeProcessor(OfxBaseProcessor):
    account_name = "ce"
    command_name = "ce"
    line_class = CeLine


def main(filename, keep):
    """Import CE bank statement (OFX file)."""
    CeProcessor(filename).push_to_ynab(keep)
