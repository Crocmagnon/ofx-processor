# ofx-processor

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ofx-processor)
![PyPI - Format](https://img.shields.io/pypi/format/ofx-processor)
![PyPI - Status](https://img.shields.io/pypi/status/ofx-processor)

## Install

```shell
python -m pip install ofx-processor
```

https://pypi.org/project/ofx-processor/

## Usage

```
Usage: ynab [OPTIONS] COMMAND [ARGS]...

  Import your data to YNAB with the processors listed below or manage your
  config.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  config   Manage configuration.
  bpvf     Import BPVF bank statement (OFX file).
  ce       Import CE bank statement (OFX file).
  lcl      Import LCL bank statement (OFX file).
  revolut  Import Revolut bank statement (CSV file).
```

All transactions will be pushed to YNAB. If this is your first time using the script,
it will open a generated config file for you to fill up.

The account and budget UUID are found in the YNAB url when using the web app.

The file passed in parameter will be deleted unless specified (`--keep` option on each import command)

## Versions

This project follows [Semantic Versioning](https://semver.org/).

## Development
### Release
```shell
inv full-test
poetry version <major/minor/patch>
git add .
git commit
inv tag <version>
inv publish publish-docker
```

# Reuse
If you do reuse my work, please consider linking back to this repository 🙂