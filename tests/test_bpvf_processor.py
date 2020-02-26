import unittest

from ofx_processor.processors.bpvf import BpvfLine


class MyTestCase(unittest.TestCase):
    def test_process_name_and_memo_no_change(self):
        name = "business"
        memo = "2020-01-17"

        result_name, result_memo = BpvfLine._process_name_and_memo(name, memo)
        self.assertEqual(result_name, name)
        self.assertEqual(result_memo, memo)

    def test_process_name_and_memo_change_required_with_conversion(self):
        name = "150120 CB****5874"
        memo = "GUY AND SONS   FR LYON 0,90EUR 1 EURO = 1,000000"

        expected_name = "GUY AND SONS   FR LYON"
        expected_memo = "150120 CB****5874 0,90EUR 1 EURO = 1,000000"

        result_name, result_memo = BpvfLine._process_name_and_memo(name, memo)
        self.assertEqual(result_name, expected_name)
        self.assertEqual(result_memo, expected_memo)

    def test_process_name_and_memo_change_required_no_conversion(self):
        name = "150120 CB****5874"
        memo = "Dott           75PARIS"

        expected_name = "Dott           75PARIS"
        expected_memo = "150120 CB****5874"

        result_name, result_memo = BpvfLine._process_name_and_memo(name, memo)
        self.assertEqual(result_name, expected_name)
        self.assertEqual(result_memo, expected_memo)


if __name__ == "__main__":
    unittest.main()
