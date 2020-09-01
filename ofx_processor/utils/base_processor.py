import os
from collections import defaultdict

import click
from ofxtools.models import STMTTRN

from ofx_processor.utils import ynab


class BaseLine:
    def __init__(self, data: STMTTRN = None):
        self.data = data  # type: STMTTRN

    def get_date(self):
        raise NotImplementedError  # pragma: nocover

    def get_amount(self):
        raise NotImplementedError  # pragma: nocover

    def get_memo(self):
        raise NotImplementedError  # pragma: nocover

    def get_payee(self):
        raise NotImplementedError  # pragma: nocover

    def to_ynab_transaction(self, transaction_ids):
        date = self.get_date()
        payee = self.get_payee()
        memo = self.get_memo()
        amount = self.get_amount()
        import_id = f"YNAB:{amount}:{date}"
        transaction_ids[import_id] += 1
        occurrence = transaction_ids[import_id]
        import_id = f"{import_id}:{occurrence}"
        ynab_transaction = {
            "date": date,
            "amount": amount,
            "payee_name": payee,
            "memo": memo,
            "import_id": import_id,
        }
        return ynab_transaction


class BaseProcessor:
    line_class = BaseLine
    account_name = None

    def __init__(self, filename):
        self.filename = filename
        self.iterable = self.parse_file()
        self.transaction_ids = defaultdict(int)

    def parse_file(self):
        return []  # pragma: nocover

    def push_to_ynab(self, keep=True):
        transactions = self.get_transactions()
        click.secho(f"Processed {len(transactions)} transactions total.", fg="blue")
        ynab.push_transactions(transactions, account=self.account_name)
        if not keep:
            os.unlink(self.filename)

    def get_transactions(self):
        return list(map(self._get_transaction, self.iterable))

    def _get_transaction(self, data):
        line = self.line_class(data)
        return line.to_ynab_transaction(self.transaction_ids)
