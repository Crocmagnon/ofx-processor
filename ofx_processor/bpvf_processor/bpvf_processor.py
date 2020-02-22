import re

from ofx_processor.utils.processor import Processor, Line


def _process_name_and_memo(name, memo):
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


class BpvfLine(Line):
    def __init__(self, data=None):
        super(BpvfLine, self).__init__(data)

    def get_date(self):
        return self.data.dtposted.isoformat().split("T")[0]

    def get_amount(self):
        return int(self.data.trnamt * 1000)

    def get_memo(self):
        return _process_name_and_memo(self.data.name, self.data.memo)[1]

    def get_payee(self):
        return _process_name_and_memo(self.data.name, self.data.memo)[0]


class BpvfProcessor(Processor):
    line_class = BpvfLine
