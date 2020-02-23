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
            if item.endswith("Processor") and item != "Processor":
                cls = getattr(module, item)
                cli.add_command(cls.main)
