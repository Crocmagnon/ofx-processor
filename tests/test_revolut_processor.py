import datetime
import unittest

from ofx_processor.processors.revolut import (
    _amount_str_to_float,
    RevolutLine,
)


class RevolutProcessorTestCase(unittest.TestCase):
    def test_process_amount_with_one_decimal_place(self):
        amount = "3,4"
        expected = 3.4
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_process_amount_with_two_decimal_places(self):
        amount = "3,41"
        expected = 3.41
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_process_amount_with_empty_string(self):
        amount = ""
        expected = ""
        self.assertEqual(_amount_str_to_float(amount), expected)

    def test_process_memo_with_category_and_rate(self):
        line = {"Category": "category name", "Exchange Rate": "exchange rate"}
        expected = "category name - exchange rate"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_process_memo_with_only_category(self):
        line = {"Category": "category name", "Exchange Rate": ""}
        expected = "category name"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_process_memo_with_only_rate(self):
        line = {"Category": "", "Exchange Rate": "exchange rate"}
        expected = "exchange rate"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_process_memo_with_missing_keys(self):
        line = {"Category": "category name"}
        expected = "category name"
        self.assertEqual(RevolutLine(line).get_memo(), expected)

    def test_process_date(self):
        line = {"Completed Date": "January 16"}
        current_year = datetime.date.today().year
        expected = f"{current_year}-01-16"
        self.assertEqual(RevolutLine(line).get_date(), expected)

    def test_process_date_other_year(self):
        line = {"Completed Date": "January 16 2019"}
        expected = f"2019-01-16"
        self.assertEqual(RevolutLine(line).get_date(), expected)

    def test_process_inflow(self):
        line = {"Paid In (EUR)": "3,42"}
        expected = 3.42
        self.assertEqual(RevolutLine(line)._process_inflow(), expected)

    def test_process_outflow(self):
        line = {"Paid Out (EUR)": "8,42"}
        expected = 8.42
        self.assertEqual(RevolutLine(line)._process_outflow(), expected)


if __name__ == "__main__":
    unittest.main()
