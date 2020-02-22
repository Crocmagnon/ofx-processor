import click

import ofx_processor.bpvf_processor.main as bpvf
import ofx_processor.revolut_processor.main as revolut
from ofx_processor.utils import ynab

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass


cli.add_command(bpvf.cli, name="bpvf")
cli.add_command(revolut.cli, name="revolut")
cli.add_command(ynab.config, name="config")

if __name__ == "__main__":
    cli()
