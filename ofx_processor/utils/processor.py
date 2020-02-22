from collections import defaultdict

import click

from ofx_processor.utils import ynab


class Line:
    data = None

    def __init__(self, data=None):
        self.data = data

    def get_date(self):
        pass

    def get_amount(self):
        pass

    def get_memo(self):
        pass

    def get_payee(self):
        pass

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


class Processor:
    transaction_ids = defaultdict(int)
    line_class = Line
    account_name = None

    def __init__(self, filename):
        self.filename = filename
        self.iterable = self.parse_file()

    def parse_file(self):
        return []

    def push_to_ynab(self):
        transactions = self.get_transactions()
        click.secho(f"Processed {len(transactions)} transactions total.", fg="blue")
        ynab.push_transactions(transactions, account=self.account_name)

    def get_transactions(self):
        return list(map(self._get_transaction, self.iterable))

    def _get_transaction(self, data):
        line = self.line_class(data)
        return line.to_ynab_transaction(self.transaction_ids)
