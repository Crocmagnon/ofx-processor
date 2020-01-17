import datetime
import unittest

from ofx_processor.revolut_processor.main import (
    process_amount,
    process_memo,
    process_date,
    process_inflow,
    process_outflow,
)


class RevolutProcessorTestCase(unittest.TestCase):
    def test_process_amount_with_one_decimal_place(self):
        amount = "3,4"
        expected = 3.4
        self.assertEqual(process_amount(amount), expected)

    def test_process_amount_with_two_decimal_places(self):
        amount = "3,41"
        expected = 3.41
        self.assertEqual(process_amount(amount), expected)

    def test_process_amount_with_empty_string(self):
        amount = ""
        expected = ""
        self.assertEqual(process_amount(amount), expected)

    def test_process_memo_with_category_and_rate(self):
        line = {"Category": "category name", "Exchange Rate": "exchange rate"}
        expected = "category name - exchange rate"
        self.assertEqual(process_memo(line), expected)

    def test_process_memo_with_only_category(self):
        line = {"Category": "category name", "Exchange Rate": ""}
        expected = "category name"
        self.assertEqual(process_memo(line), expected)

    def test_process_memo_with_only_rate(self):
        line = {"Category": "", "Exchange Rate": "exchange rate"}
        expected = "exchange rate"
        self.assertEqual(process_memo(line), expected)

    def test_process_memo_with_missing_keys(self):
        line = {"Category": "category name"}
        expected = "category name"
        self.assertEqual(process_memo(line), expected)

    def test_process_date(self):
        line = {"Completed Date": "January 16"}
        current_year = datetime.date.today().year
        expected = f"{current_year}-01-16"
        self.assertEqual(process_date(line), expected)

    def test_process_date_other_year(self):
        line = {"Completed Date": "January 16 2019"}
        expected = f"2019-01-16"
        self.assertEqual(process_date(line), expected)

    def test_process_inflow(self):
        line = {"Paid In (EUR)": "3,42"}
        expected = 3.42
        self.assertEqual(process_inflow(line), expected)

    def test_process_outflow(self):
        line = {"Paid Out (EUR)": "8,42"}
        expected = 8.42
        self.assertEqual(process_outflow(line), expected)


if __name__ == "__main__":
    unittest.main()
