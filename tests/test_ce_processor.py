import json
import unittest

from ofx_processor.processors.ce import CeProcessor


class CeProcessorTestCase(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            CeProcessor("filenotfound.ofx").get_transactions()

    def test_file(self):
        transactions = CeProcessor("tests/samples/ce.ofx").get_transactions()
        with open("tests/samples/ce_expected.json") as f:
            expected_transactions = json.load(f)

        self.assertListEqual(transactions, expected_transactions)


if __name__ == "__main__":
    unittest.main()  # pragma: nocover
