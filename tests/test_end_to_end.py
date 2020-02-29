import unittest
from unittest import mock
from unittest.mock import call

from click.testing import CliRunner

from ofx_processor.processors.bpvf import BpvfProcessor
from ofx_processor.processors.ce import CeProcessor
from ofx_processor.processors.revolut import RevolutProcessor
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
