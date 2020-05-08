import collections
import importlib
import pkgutil

import click

from ofx_processor import processors


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
                method = click.option(
                    "--keep/--no-keep",
                    help="Keep the file after processing it.",
                    default=False,
                    show_default=True,
                )(method)
                method = click.argument("filename")(method)
                method = click.command(cls.command_name)(method)

                cli.add_command(method)


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands
