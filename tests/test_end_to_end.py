import json
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import call

from click.testing import CliRunner

import ofx_processor.utils.config
from ofx_processor.utils import utils, ynab
from ofx_processor.utils.config import config


class UtilsTestCase(unittest.TestCase):
    """
    This class needs to run before any other that imports
    ofx_processor.main.cli because it tests import time stuff.
    """

    def test_discover_processors(self):
        expected_names = ["config", "bpvf", "lcl", "ce", "revolut"]
        runner = CliRunner()
        with mock.patch("click.core.Group.add_command") as add_command:
            from ofx_processor.main import cli

            calls = [call(config, name="config")]
            runner.invoke(cli, ["--help"])
            add_command.assert_has_calls(calls, any_order=True)
            self.assertEqual(
                set(map(lambda call_: call_[0][0].name, add_command.call_args_list)),
                set(expected_names),
            )


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        cli.add_command(ofx_processor.utils.config.config, name="config")
        utils.discover_processors(cli)
        self.cli = cli

    @mock.patch("click.edit")
    @mock.patch(
        "ofx_processor.utils.config.DEFAULT_CONFIG_DIR",
        os.path.join("tests", "samples"),
    )
    def test_config_edit(self, edit):
        runner = CliRunner()
        runner.invoke(self.cli, ["config", "edit"])

        expected_filename = os.path.join("tests", "samples", "config.ini")
        edit.assert_called_once_with(filename=expected_filename)

    @mock.patch("click.edit")
    @mock.patch(
        "ofx_processor.utils.config.DEFAULT_CONFIG_FILENAME",
        "config_broken_duplicate_key.ini",
    )
    @mock.patch(
        "ofx_processor.utils.config.DEFAULT_CONFIG_DIR",
        os.path.join("tests", "samples"),
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
            with mock.patch("ofx_processor.utils.config.DEFAULT_CONFIG_FILENAME", name):
                runner = CliRunner()
                result = runner.invoke(
                    self.cli, ["revolut", "-f", "tests/samples/revolut.csv", "--keep"]
                )
                expected_filename = ofx_processor.utils.config.get_config_file_name()
                self.assertIn(
                    "Error while parsing config file",
                    result.output,
                    f"config_file: {name}",
                )
                edit.assert_called_with(filename=expected_filename)

    @mock.patch("ofx_processor.utils.config.DEFAULT_CONFIG_FILENAME", "file.ini")
    @mock.patch(
        "ofx_processor.utils.config.DEFAULT_CONFIG_DIR",
        os.path.join("some", "config", "folder"),
    )
    def test_get_config_file_name(self):
        expected = os.path.join("some", "config", "folder", "file.ini")
        self.assertEqual(ofx_processor.utils.config.get_config_file_name(), expected)

    @mock.patch("requests.post")
    @mock.patch("click.edit")
    @mock.patch("os.makedirs")
    @mock.patch("ofx_processor.utils.config.DEFAULT_CONFIG_FILENAME", "notfound.ini")
    @mock.patch(
        "ofx_processor.utils.config.DEFAULT_CONFIG_DIR",
        os.path.join("tests", "samples"),
    )
    def test_missing_config_file(self, makedirs, edit, *args):
        runner = CliRunner()
        with mock.patch(
            "ofx_processor.utils.config.open", mock.mock_open()
        ) as mock_file:
            result = runner.invoke(
                self.cli, ["revolut", "-f", "tests/samples/revolut.csv", "--keep"]
            )
            mock_file.assert_called_once()
        makedirs.assert_called_once_with(
            ofx_processor.utils.config.DEFAULT_CONFIG_DIR, exist_ok=True
        )
        self.assertIn("Editing config file", result.output)
        expected_filename = ofx_processor.utils.config.get_config_file_name()
        edit.assert_called_once_with(filename=expected_filename)
        # post.assert_not_called()


@mock.patch(
    "ofx_processor.utils.config.DEFAULT_CONFIG_DIR", os.path.join("tests", "samples")
)
class DataTestCase(unittest.TestCase):
    def setUp(self):
        from ofx_processor.main import cli

        # This is run at import time and the cli module is already imported before this test
        # so we need to re-run the add_command to make it available.
        cli.add_command(ofx_processor.utils.config.config, name="config")
        utils.discover_processors(cli)
        self.cli = cli

    @mock.patch("requests.post")
    def test_file_is_deleted_by_default(self, post):
        post.return_value.status_code = 201
        runner = CliRunner()
        revolut_csv = "tests/samples/revolut.csv"
        backup_file = "tests/samples/backup.csv"

        # backup the file, other tests will need it
        shutil.copyfile(revolut_csv, backup_file)

        try:
            self.assertTrue(os.path.isfile(revolut_csv))
            result = runner.invoke(self.cli, ["revolut", "-f", revolut_csv])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(os.path.isfile(revolut_csv))
        finally:
            # restore the file so other tests can rely on it, whatever happens
            shutil.copyfile(backup_file, revolut_csv)
            os.unlink(backup_file)

    @mock.patch("requests.post")
    def test_file_is_kept_with_option(self, post):
        post.return_value.status_code = 201
        runner = CliRunner()
        revolut_csv = "tests/samples/revolut.csv"
        backup_file = "tests/samples/backup.csv"

        # backup the file, other tests will need it
        shutil.copyfile(revolut_csv, backup_file)

        try:
            self.assertTrue(os.path.isfile(revolut_csv))
            result = runner.invoke(
                self.cli, ["revolut", "--filename", revolut_csv, "--keep"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.isfile(revolut_csv))
        finally:
            # restore the file so other tests can rely on it, whatever happens
            shutil.copyfile(backup_file, revolut_csv)
            os.unlink(backup_file)

    @mock.patch("requests.post")
    def test_revolut_sends_data_only_created(self, post):
        post.return_value.status_code = 201
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
                    {"id": "created:12", "matched_transaction_id": None},
                ],
                "duplicate_import_ids": [],
            }
        }

        runner = CliRunner()
        result = runner.invoke(
            self.cli, ["revolut", "-f", "tests/samples/revolut.csv", "--keep"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 10 transactions total.", result.output)
        self.assertIn("10 transactions created in YNAB.", result.output)
        self.assertNotIn("transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_some_created_some_duplicates(self, post):
        post.return_value.status_code = 201
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
                    "duplicate:12",
                ],
            }
        }

        runner = CliRunner()
        result = runner.invoke(
            self.cli, ["revolut", "-f", "tests/samples/revolut.csv", "--keep"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 10 transactions total.", result.output)
        self.assertIn("3 transactions created in YNAB.", result.output)
        self.assertIn("7 transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_revolut_sends_data_only_duplicates(self, post):
        post.return_value.status_code = 201
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
                    "duplicate:10",
                ],
            }
        }

        runner = CliRunner()
        result = runner.invoke(
            self.cli, ["revolut", "-f", "tests/samples/revolut.csv", "--keep"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Processed 10 transactions total.", result.output)
        self.assertNotIn("transactions created in YNAB.", result.output)
        self.assertIn("10 transactions ignored (duplicates).", result.output)

    @mock.patch("requests.post")
    def test_bpvf_sends_to_ynab(self, post):
        post.return_value.status_code = 201
        with open("tests/samples/bpvf_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["bpvf", "-f", "tests/samples/bpvf.ofx", "--keep"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )

    @mock.patch("requests.post")
    def test_ce_sends_to_ynab(self, post):
        post.return_value.status_code = 201
        with open("tests/samples/ce_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["ce", "-f", "tests/samples/ce.ofx", "--keep"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )

    @mock.patch("requests.post")
    def test_lcl_sends_to_ynab(self, post):
        post.return_value.status_code = 201
        with open("tests/samples/lcl_transactions.json", encoding="utf-8") as f:
            expected_data = json.load(f)

        expected_headers = {"Authorization": f"Bearer <YOUR API TOKEN>"}
        expected_url = f"{ynab.BASE_URL}/budgets/<YOUR BUDGET ID>/transactions"

        runner = CliRunner()
        runner.invoke(self.cli, ["lcl", "-f", "tests/samples/lcl.ofx", "--keep"])

        post.assert_called_once_with(
            expected_url, json=expected_data, headers=expected_headers
        )
