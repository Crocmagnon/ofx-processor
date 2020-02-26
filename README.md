# ofx-processor

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
