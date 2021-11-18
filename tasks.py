from pathlib import Path

from invoke import task

BASE_DIR = Path(__file__).parent.resolve(strict=True)


@task
def test(ctx):
    with ctx.cd(BASE_DIR):
        ctx.run(f"pytest --cov=.", pty=True, echo=True)
