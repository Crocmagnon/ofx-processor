import click

from ofx_processor.bpvf_processor import bpvf_cli
from ofx_processor.ce_processor import ce_cli
from ofx_processor.revolut_processor import revolut_cli
from ofx_processor.utils import ynab

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass


cli.add_command(bpvf_cli.main, name="bpvf")
cli.add_command(revolut_cli.main, name="revolut")
cli.add_command(ce_cli.main, name="ce")
cli.add_command(ynab.config, name="config")

if __name__ == "__main__":
    cli()
