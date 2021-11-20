import json
import unittest
from unittest import mock

import ofx_processor.utils.config
from ofx_processor.utils import ynab


class YNABIntegrationTestCase(unittest.TestCase):
    @mock.patch("requests.post")
    def test_data_sent_to_ynab(self, post):
        post.return_value.status_code = 201
        ofx_processor.utils.config.DEFAULT_CONFIG_DIR = "tests/samples"

        with open("tests/samples/revolut_expected.json", encoding="utf-8") as f:
            transactions = json.load(f)
        with open("tests/samples/revolut_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        ynab.push_transactions(transactions, "revolut")

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )

    @mock.patch("requests.post")
    def test_no_data_to_send(self, post):
        ynab.push_transactions([], "")
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()  # pragma: nocover
