import click

from ofx_processor import downloaders
from ofx_processor.utils import config
from ofx_processor.utils.utils import OrderedGroup, discover_processors

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS, cls=OrderedGroup)
@click.version_option()
def cli():
    """
    Import your data to YNAB with the processors listed below
    or manage your config.
    """


cli.add_command(config.config, name="config")
discover_processors(cli)

if __name__ == "__main__":
    cli()  # pragma: nocover
