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
    * Declare a static main function in this class,
      which must be a click command

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
                cli.add_command(cls.main)


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands
