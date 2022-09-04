import collections
import importlib
import inspect
import pkgutil

import click

from ofx_processor import processors

ARG_TO_OPTION = {
    "keep": click.option(
        "--keep/--no-keep",
        help="Keep the file after processing it.",
        default=False,
        show_default=True,
    ),
    "send_method": click.option(
        "send_method",
        "-s",
        "--send",
        help=(
            "Send the reconciled amount via the chosen method. "
            "Accepted methods: sms, email"
        ),
        default="",
        show_default=True,
    ),
    "download": click.option(
        "--download/--no-download",
        help="Download the file automatically.",
        default=False,
        show_default=True,
    ),
    "filename": click.option(
        "-f",
        "--filename",
        help="Use specified file.",
        default="",
        show_default=True,
    ),
    "push_to_ynab": click.option(
        "push_to_ynab",
        "--push/--no-push",
        help="Push the data to YNAB.",
        default=True,
        show_default=True,
    ),
}


def discover_processors(cli: click.Group):
    """
    Discover processors.

    To be discovered, processors must:
    * Be in the `processors` package.
    * Declare a <BankName>Processor class
    * Declare a main function in the module, outside of the class.
      The main function must not be a click command, decorators will be added on the fly.
      The main function must accept two parameters:
      * filename: str, containing the name of the file to process, as passed on the command line
      * keep: boolean, whether to keep the file after processing it or not

    :param cli: The main CLI to add discovered processors to.
    """
    prefix = processors.__name__ + "."
    for module in pkgutil.iter_modules(processors.__path__, prefix):
        module = importlib.import_module(module.name)
        for item in dir(module):
            if (
                item.endswith("Processor")
                and item != "Processor"
                and "Base" not in item
            ):
                cls = getattr(module, item)
                assert hasattr(
                    module, "main"
                ), "There must be a main function in the processor module."
                assert hasattr(
                    cls, "command_name"
                ), "You must add a command_name member to your processor class."

                # Apply default decorators
                method = getattr(module, "main")
                method_args = inspect.getfullargspec(method).args
                for arg in method_args:
                    if arg in ARG_TO_OPTION:
                        method = ARG_TO_OPTION[arg](method)
                method = click.command(cls.command_name)(method)

                cli.add_command(method)


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands
