# ofx-processor

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=bugs)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=code_smells)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=coverage)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=duplicated_lines_density)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=ncloc)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=alert_status)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=security_rating)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=Crocmagnon_ofx-processor&metric=sqale_index)](https://sonarcloud.io/dashboard?id=Crocmagnon_ofx-processor)
    
## Usage

```shell script
Usage: ynab [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  bpvf     Process BPVF bank statement (OFX)
  ce       Process CE bank statement (OFX)
  config
  revolut  Process Revolut bank statement (CSV)
```

All transactions will be pushed to YNAB. If this is your first time using the script,
it will open a generated config file for you to fill up.

The account and budget UUID are found in the YNAB url when using the web app.
