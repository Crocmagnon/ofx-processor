import unittest
from unittest import mock
from unittest.mock import call

from click.testing import CliRunner

from ofx_processor.processors.bpvf import BpvfProcessor
from ofx_processor.processors.ce import CeProcessor
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
        runner = CliRunner()
        with mock.patch("click.core.Group.add_command") as add_command:
            from ofx_processor.main import cli

            runner.invoke(cli, ["--help"])
            calls = [
                call(ce_main),
                call(bpvf_main),
                call(revolut_main),
                call(config, name="config"),
            ]
            add_command.assert_has_calls(calls, any_order=True)


class ConfigEditTestCase(unittest.TestCase):
    @mock.patch("click.edit")
    def test_config_edit(self, edit):
        config_dir = "tests/samples"
        ynab.DEFAULT_CONFIG_DIR = config_dir
        expected_filename = f"{config_dir}/config.ini"
        runner = CliRunner()
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        cli.add_command(ynab.config, name="config")

        runner.invoke(cli, ["config", "edit"])
        edit.assert_called_once_with(filename=expected_filename)


class DataTestCase(unittest.TestCase):
    @mock.patch("requests.post")
    def test_revolut_sends_data_only_created(self, post):
        ynab.DEFAULT_CONFIG_DIR = "tests/samples"
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
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        utils.discover_processors(cli)

        runner = CliRunner()
        result = runner.invoke(cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertIn("9 transactions created in YNAB.", result.output)
        self.assertNotIn("transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_some_created_some_duplicates(self, post):
        ynab.DEFAULT_CONFIG_DIR = "tests/samples"
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
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        utils.discover_processors(cli)

        runner = CliRunner()
        result = runner.invoke(cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertIn("3 transactions created in YNAB.", result.output)
        self.assertIn("6 transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_only_duplicates(self, post):
        ynab.DEFAULT_CONFIG_DIR = "tests/samples"
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
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        utils.discover_processors(cli)

        runner = CliRunner()
        result = runner.invoke(cli, ["revolut", "tests/samples/revolut.csv"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 9 transactions total.", result.output)
        self.assertNotIn("transactions created in YNAB.", result.output)
        self.assertIn("9 transactions ignored (duplicates).", result.output)
