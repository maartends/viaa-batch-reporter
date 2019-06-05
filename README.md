# Batch reporting script

Script to report on batches in the archiving backend.

## Installation

*TODO*

- clone
- run

## Usage

```shell
usage: batch-reporter [-h] [-m MTD] batch

Report on batches

positional arguments:
  batch              Specify batchname.

optional arguments:
  -h, --help         show this help message and exit
  -m MTD, --mtd MTD  Filepath to mtd (csv) file.
```
 For example:

    $ report batch123 --mtd /home/alice/batch123.mtd
