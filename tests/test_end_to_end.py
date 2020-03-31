import json
import os
import unittest
from unittest import mock
from unittest.mock import call

from click.testing import CliRunner

from ofx_processor.processors.bpvf import BpvfProcessor
from ofx_processor.processors.ce import CeProcessor
from ofx_processor.processors.lcl import LclProcessor
from ofx_processor.processors.revolut import RevolutProcessor
from ofx_processor.utils import utils
from ofx_processor.utils import ynab
from ofx_processor.utils.ynab import config


class UtilsTestCase(unittest.TestCase):
    """
    This class needs to run before any other that imports
    ofx_processor.main.cli because it tests import time stuff.
    """

    @staticmethod
    def test_discover_processors():
        ce_main = CeProcessor.main
        bpvf_main = BpvfProcessor.main
        revolut_main = RevolutProcessor.main
        lcl_main = LclProcessor.main
        runner = CliRunner()
        with mock.patch("click.core.Group.add_command") as add_command:
            from ofx_processor.main import cli

            runner.invoke(cli, ["--help"])
            calls = [
                call(ce_main),
                call(bpvf_main),
                call(revolut_main),
                call(lcl_main),
                call(config, name="config"),
            ]
            add_command.assert_has_calls(calls, any_order=True)


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        cli.add_command(ynab.config, name="config")
        utils.discover_processors(cli)
        self.cli = cli

    @mock.patch("click.edit")
    @mock.patch(
        "ofx_processor.utils.ynab.DEFAULT_CONFIG_DIR", os.path.join("tests", "samples")
    )
    def test_config_edit(self, edit):
        runner = CliRunner()
        runner.invoke(self.cli, ["config", "edit"])

        expected_filename = os.path.join("tests", "samples", "config.ini")
        edit.assert_called_once_with(filename=expected_filename)

    @mock.patch("click.edit")
    @mock.patch(
        "ofx_processor.utils.ynab.DEFAULT_CONFIG_FILENAME",
        "config_broken_duplicate_key.ini",
    )
    @mock.patch(
        "ofx_processor.utils.ynab.DEFAULT_CONFIG_DIR", os.path.join("tests", "samples")
    )
    def test_broken_config_file(self, edit):
        broken_files = [
            "config_broken_duplicate_key.ini",
            "config_broken_missing_account.ini",
            "config_broken_missing_account_key.ini",
            "config_broken_missing_budget.ini",
            "config_broken_missing_token.ini",
        ]
        for name in broken_files:
            with mock.patch("ofx_processor.utils.ynab.DEFAULT_CONFIG_FILENAME", name):
                runner = CliRunner()
                result = runner.invoke(
                    self.cli, ["revolut", "tests/samples/revolut.csv"]
                )
                expected_filename = ynab.get_config_file_name()
                self.assertIn("Error while parsing config file", result.output)
                edit.assert_called_with(filename=expected_filename)

    @mock.patch("ofx_processor.utils.ynab.DEFAULT_CONFIG_FILENAME", "file.ini")
    @mock.patch(
        "ofx_processor.utils.ynab.DEFAULT_CONFIG_DIR",
        os.path.join("some", "config", "folder"),
    )
    def test_get_config_file_name(self):
        expected = os.path.join("some", "config", "folder", "file.ini")
        self.assertEqual(ynab.get_config_file_name(), expected)

    @mock.patch("click.edit")
    @mock.patch("os.makedirs")
    @mock.patch("ofx_processor.utils.ynab.DEFAULT_CONFIG_FILENAME", "notfound.ini")
    @mock.patch(
        "ofx_processor.utils.ynab.DEFAULT_CONFIG_DIR", os.path.join("tests", "samples")
    )
    def test_missing_config_file(self, makedirs, edit):
        runner = CliRunner()
        with mock.patch("ofx_processor.utils.ynab.open", mock.mock_open()) as mock_file:
            result = runner.invoke(self.cli, ["revolut", "tests/samples/revolut.csv"])
            mock_file.assert_called_once()
        makedirs.assert_called_once_with(ynab.DEFAULT_CONFIG_DIR, exist_ok=True)
        self.assertIn("Editing config file", result.output)
        expected_filename = ynab.get_config_file_name()
        edit.assert_called_once_with(filename=expected_filename)


@mock.patch(
    "ofx_processor.utils.ynab.DEFAULT_CONFIG_DIR", os.path.join("tests", "samples")
)
class DataTestCase(unittest.TestCase):
    def setUp(self):
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        cli.add_command(ynab.config, name="config")
        utils.discover_processors(cli)
        self.cli = cli

    @mock.patch("requests.post")
    def test_revolut_sends_data_only_created(self, post):
        post.return_value.json.return_value = {
            "data": {
                "transactions": [
                    {
                        "id": "ynab_existing:1",
                        "matched_transaction_id": "imported_matched:2",
                    },
                    {
                        "id": "imported_matched:2",
                        "matched_transaction_id": "ynab_existing:1",
                    },
                    {
                        "id": "imported_matched:3",
                        "matched_transaction_id": "ynab_existing:4",
                    },
                    {
                        "id": "ynab_existing:4",
                        "matched_transaction_id": "imported_matched:3",
                    },
                    {"id": "created:5", "matched_transaction_id": None},
                    {"id": "created:6", "matched_transaction_id": None},
                    {"id": "created:7", "matched_transaction_id": None},
                    {"id": "created:8", "matched_transaction_id": None},
                    {"id": "created:9", "matched_transaction_id": None},
                    {"id": "created:10", "matched_transaction_id": None},
                    {"id": "created:11", "matched_transaction_id": None},
                ],
                "duplicate_import_ids": [],
            }
        }

        runner = CliRunner()
        result = runner.invoke(self.cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertIn("9 transactions created in YNAB.", result.output)
        self.assertNotIn("transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_some_created_some_duplicates(self, post):
        post.return_value.json.return_value = {
            "data": {
                "transactions": [
                    {
                        "id": "ynab_existing:1",
                        "matched_transaction_id": "imported_matched:2",
                    },
                    {
                        "id": "imported_matched:2",
                        "matched_transaction_id": "ynab_existing:1",
                    },
                    {
                        "id": "imported_matched:3",
                        "matched_transaction_id": "ynab_existing:4",
                    },
                    {
                        "id": "ynab_existing:4",
                        "matched_transaction_id": "imported_matched:3",
                    },
                    {"id": "created:5", "matched_transaction_id": None},
                ],
                "duplicate_import_ids": [
                    "duplicate:6",
                    "duplicate:7",
                    "duplicate:8",
                    "duplicate:9",
                    "duplicate:10",
                    "duplicate:11",
                ],
            }
        }

        runner = CliRunner()
        result = runner.invoke(self.cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertIn("3 transactions created in YNAB.", result.output)
        self.assertIn("6 transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_only_duplicates(self, post):
        post.return_value.json.return_value = {
            "data": {
                "transactions": [],
                "duplicate_import_ids": [
                    "duplicate:1",
                    "duplicate:2",
                    "duplicate:3",
                    "duplicate:4",
                    "duplicate:5",
                    "duplicate:6",
                    "duplicate:7",
                    "duplicate:8",
                    "duplicate:9",
                ],
            }
        }

        runner = CliRunner()
        result = runner.invoke(self.cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertNotIn("transactions created in YNAB.", result.output)
        self.assertIn("9 transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_bpvf_sends_to_ynab(self, post):
        with open("tests/samples/bpvf_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["bpvf", "tests/samples/bpvf.ofx"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )

    @mock.patch("requests.post")
    def test_ce_sends_to_ynab(self, post):
        with open("tests/samples/ce_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["ce", "tests/samples/ce.ofx"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )

    @mock.patch("requests.post")
    def test_lcl_sends_to_ynab(self, post):
        with open("tests/samples/lcl_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["lcl", "tests/samples/lcl.ofx"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )
