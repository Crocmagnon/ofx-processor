import datetime
import json
import unittest

from ofx_processor.processors.lcl import LclLine, LclProcessor
from tests.utils import OfxTransaction


class LclLineTestCase(unittest.TestCase):
    def test_get_name(self):
        name = "VIR INST"
        transaction = OfxTransaction(name=name)

        result_name = LclLine(transaction).get_payee()
        self.assertEqual(result_name, name)

    def test_get_memo(self):
        memo = "VIR INST"
        transaction = OfxTransaction(memo=memo)

        result_memo = LclLine(transaction).get_memo()
        self.assertEqual(result_memo, memo)

    def test_get_date(self):
        transaction = OfxTransaction(dtposted=datetime.datetime(2020, 1, 23, 1, 2, 3))
        expected_date = "2020-01-23"

        result_date = LclLine(transaction).get_date()
        self.assertEqual(result_date, expected_date)

    def test_get_amount_positive(self):
        transaction = OfxTransaction(trnamt=52.2)
        expected_amount = 52200

        result_amount = LclLine(transaction).get_amount()
        self.assertEqual(result_amount, expected_amount)

    def test_get_amount_negative(self):
        transaction = OfxTransaction(trnamt=-52.2)
        expected_amount = -52200

        result_amount = LclLine(transaction).get_amount()
        self.assertEqual(result_amount, expected_amount)


class LclProcessorTestCase(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            LclProcessor("filenotfound.ofx").get_transactions()

    def test_file(self):
        transactions = LclProcessor("tests/samples/lcl.ofx").get_transactions()
        with open("tests/samples/lcl_expected.json") as f:
            expected_transactions = json.load(f)

        self.assertListEqual(transactions, expected_transactions)

    def test_file_as_downloaded(self):
        transactions = LclProcessor(
            "tests/samples/lcl_as_downloaded.ofx"
        ).get_transactions()
        with open("tests/samples/lcl_expected.json") as f:
            expected_transactions = json.load(f)

        self.assertListEqual(transactions, expected_transactions)

    def test_file_malformed(self):
        with self.assertRaises(SystemExit):
            LclProcessor("tests/samples/lcl_malformed.ofx")


if __name__ == "__main__":
    unittest.main()  # pragma: nocover
