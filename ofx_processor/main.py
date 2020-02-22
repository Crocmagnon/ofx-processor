import click

import ofx_processor.bpvf_processor.main as bpvf
import ofx_processor.revolut_processor.main as revolut

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass


cli.add_command(bpvf.cli, name="bpvf")
cli.add_command(revolut.cli, name="revolut")

if __name__ == "__main__":
    cli()
