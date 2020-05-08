# ofx-processor

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ofx-processor)
![PyPI - Format](https://img.shields.io/pypi/format/ofx-processor)
![PyPI - Status](https://img.shields.io/pypi/status/ofx-processor)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Crocmagnon/ofx-processor?include_prereleases)
![License](https://img.shields.io/github/license/Crocmagnon/ofx-processor)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Crocmagnon/ofx-processor/Test%20&%20publish)
![Sonar Coverage](https://img.shields.io/sonar/coverage/Crocmagnon_ofx-processor?server=https%3A%2F%2Fsonarcloud.io)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=bugs)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=code_smells)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=alert_status)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=security_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=sqale_index)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)


## Usage

```shell script
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