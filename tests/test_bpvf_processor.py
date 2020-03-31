import datetime
import json
import unittest

from ofx_processor.processors.bpvf import BpvfLine, BpvfProcessor
from tests.utils import OfxTransaction


class BpvfLineTestCase(unittest.TestCase):
    def test_process_name_and_memo_no_change(self):
        name = "business"
        memo = "2020-01-17"
        transaction = OfxTransaction(name=name, memo=memo)

        line = BpvfLine(transaction)
        result_name = line.get_payee()
        result_memo = line.get_memo()
        self.assertEqual(result_name, name)
        self.assertEqual(result_memo, memo)

    def test_process_name_and_memo_change_required_with_conversion(self):
        name = "150120 CB****5874"
        memo = "GUY AND SONS   FR LYON 0,90EUR 1 EURO = 1,000000"
        transaction = OfxTransaction(name=name, memo=memo)

        expected_name = "GUY AND SONS   FR LYON"
        expected_memo = "150120 CB****5874 0,90EUR 1 EURO = 1,000000"

        line = BpvfLine(transaction)
        result_name = line.get_payee()
        result_memo = line.get_memo()
        self.assertEqual(result_name, expected_name)
        self.assertEqual(result_memo, expected_memo)

    def test_process_name_and_memo_change_required_no_conversion(self):
        name = "150120 CB****5874"
        memo = "Dott           75PARIS"
        transaction = OfxTransaction(name=name, memo=memo)

        expected_name = "Dott           75PARIS"
        expected_memo = "150120 CB****5874"

        line = BpvfLine(transaction)
        result_name = line.get_payee()
        result_memo = line.get_memo()
        self.assertEqual(result_name, expected_name)
        self.assertEqual(result_memo, expected_memo)

    def test_get_date(self):
        transaction = OfxTransaction(dtposted=datetime.datetime(2020, 1, 23, 1, 2, 3))
        expected_date = "2020-01-23"

        result_date = BpvfLine(transaction).get_date()
        self.assertEqual(result_date, expected_date)

    def test_get_amount_positive(self):
        transaction = OfxTransaction(trnamt=52.2)
        expected_amount = 52200

        result_amount = BpvfLine(transaction).get_amount()
        self.assertEqual(result_amount, expected_amount)

    def test_get_amount_negative(self):
        transaction = OfxTransaction(trnamt=-52.2)
        expected_amount = -52200

        result_amount = BpvfLine(transaction).get_amount()
        self.assertEqual(result_amount, expected_amount)


class BpvfProcessorTestCase(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            BpvfProcessor("filenotfound.ofx").get_transactions()

    def test_file(self):
        transactions = BpvfProcessor("tests/samples/bpvf.ofx").get_transactions()
        with open("tests/samples/bpvf_expected.json") as f:
            expected_transactions = json.load(f)

        self.assertListEqual(transactions, expected_transactions)

    def test_file_malformed(self):
        with self.assertRaises(SystemExit):
            BpvfProcessor("tests/samples/bpvf_malformed.ofx")


if __name__ == "__main__":
    unittest.main()  # pragma: nocover
