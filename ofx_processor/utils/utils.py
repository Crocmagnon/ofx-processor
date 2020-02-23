import importlib
import pkgutil

import click

import ofx_processor


def discover_processors(cli: click.Group):
    """
    Discover processors. To be discovered, CLIs need to match the following structure:

    ofx_processor
    ├── __init__.py
    └── <package_name>_processor
        ├── __init__.py
        ├── <module_name>_cli.py
        └── <module_name>_processor.py

    Preferably, package_name and module_name are the same, but there is no restriction.
    Finally, a "main" function will be looked for inside the <module_name>_cli module.
    This function must be a Click command with a unique name and will be added to the
    main command line interface.

    :param cli: The main CLI to add discovered processors to.
    """
    prefix = ofx_processor.__name__ + "."
    for package in pkgutil.iter_modules(ofx_processor.__path__, prefix):
        if package.name.endswith("_processor"):
            module_prefix = package.name + "."
            package = importlib.import_module(package.name)
            for module in pkgutil.iter_modules(package.__path__, module_prefix):
                if module.name.endswith("_cli"):
                    module = importlib.import_module(module.name)
                    if "main" in dir(module):
                        cli.add_command(module.main)
