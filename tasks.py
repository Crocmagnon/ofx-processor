from pathlib import Path

from invoke import task

BASE_DIR = Path(__file__).parent.resolve(strict=True)


@task
def test(ctx):
    with ctx.cd(BASE_DIR):
        ctx.run(f"pytest", pty=True, echo=True)


@task
def test_cov(ctx):
    with ctx.cd(BASE_DIR):
        ctx.run(
            f"pytest --cov=. --cov-report term-missing:skip-covered",
            pty=True,
            echo=True,
        )


@task
def full_test(ctx):
    with ctx.cd(BASE_DIR):
        ctx.run(f"tox", pty=True, echo=True)


@task
def publish(ctx):
    with ctx.cd(BASE_DIR):
        ctx.run(f"poetry publish --build", pty=True, echo=True)
