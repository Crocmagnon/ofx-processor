import datetime
import json
import unittest

from ofx_processor.processors.revolut import (
    _amount_str_to_float,
    RevolutLine,
    RevolutProcessor,
)


class RevolutProcessorTestCase(unittest.TestCase):
    def test_convert_amount_with_one_decimal_place(self):
        amount = "3,4"
        expected = 3.4
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_convert_amount_with_two_decimal_places(self):
        amount = "3,41"
        expected = 3.41
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_convert_amount_with_empty_string(self):
        amount = ""
        expected = ""
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_get_memo_with_category_and_rate(self):
        line = {"Category": "category name", "Exchange Rate": "exchange rate"}
        expected = "category name - exchange rate"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_get_memo_with_only_category(self):
        line = {"Category": "category name", "Exchange Rate": ""}
        expected = "category name"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_get_memo_with_only_rate(self):
        line = {"Category": "", "Exchange Rate": "exchange rate"}
        expected = "exchange rate"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_get_memo_with_missing_keys(self):
        line = {"Category": "category name"}
        expected = "category name"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_get_date(self):
        line = {"Completed Date": "January 16"}
        current_year = datetime.date.today().year
        expected = f"{current_year}-01-16"
        self.assertEqual(RevolutLine(line).get_date(), expected)

    def test_get_date_other_year(self):
        line = {"Completed Date": "January 16 2019"}
        expected = f"2019-01-16"
        self.assertEqual(RevolutLine(line).get_date(), expected)

    def test_get_amount_inflow(self):
        line = {"Paid In (EUR)": "3,42"}
        expected = 3420
        self.assertEqual(RevolutLine(line).get_amount(), expected)

    def test_get_amount_outflow(self):
        line = {"Paid Out (EUR)": "8,42"}
        expected = -8420
        self.assertEqual(RevolutLine(line).get_amount(), expected)

    def test_get_payee(self):
        line = {"Reference": "Hello world"}
        expected = line["Reference"]
        self.assertEqual(RevolutLine(line).get_payee(), expected)


class RevolutProcessorTestCase(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            RevolutProcessor("notfound.csv").get_transactions()

    def test_file(self):
        transactions = RevolutProcessor("tests/samples/revolut.csv").get_transactions()
        with open("tests/samples/revolut_expected.json") as f:
            expected_transactions = json.load(f)

        self.assertListEqual(transactions, expected_transactions)


if __name__ == "__main__":
    unittest.main()  # pragma: nocover
