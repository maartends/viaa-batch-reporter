# Batch reporting script

Script to report on batches in the archiving back end.

## Synopsis

Files/SIPs can be delivered to meemoo in the form of _batches_: a set of files
bound together by a certain attribute. Often, this grouping of files is merely
logical: there might not be a physical reason for these files to belong
together. It can be convenient however to be able to report on batches as a
whole rather than on individual files.

For this purpose, an indexed (non-standard) field exists in MediaHaven:
`Dynamic.dc_identifier_localids.batch`. This field can be queried via the
`dc_identifier_localidsbatch` query-parameter.

## Prerequisites

- Python 3
- Python 3 virtualenv

Check your Python version with:

    $ python --version

or:

    $ python3 --version

## Installation

- First, clone this repository

      $ git clone git@github.com:maartends/viaa-batch-reporter.git

  or

      $ git clone https://github.com/maartends/viaa-batch-reporter.git

### Make

- `cd` into the cloned directory:

      $ cd viaa-batch-reporter

- Then, just:

      $ make install

### Manual

- cd into the cloned directory and create a python virtual environment

      $ python3 -m venv .

    (notice the `.` at the end)

- Activate the virtual environment

      $ source bin/activate

- Install requirements

      $ pip install -r requirements.txt

- Rename `config.yml.example` to `config.yml` and fill in the
  configuration-values

      $ mv config.yml.example config.yml

- Run `help` to check if the installation succeeded

      $ ./report -h

Output should be as below.

## Usage

Before usage of the batch-reporter, the virtual environment should always be
activated. This is done via:

    $ source bin/activate

Output of `$ ./report -h`:

```
usage: batch-reporter [-h] [-g] [-m MTD] batch

Report on batches

positional arguments:
  batch              Specify batchname.

optional arguments:
  -h, --help         show this help message and exit
  -g, --glob-file    Find mtd file through glob-pattern. If set, I'll try to
                     find the mtd-file based on the batch name. Defaults to
                     false.
  -m MTD, --mtd MTD  Filepath to mtd (csv) file. Can be local or FTP-path.
```

Before running, the configuration file `config.yml` should be filled in.

Then, run with, for example:

    $ ./report batch123 --mtd /home/alice/batch123.mtd

The `mtd` parameter takes both a local filepath as well as a fully-qualified
FTP-path as input. For example:

    $ ./report batch123 --mtd ftp://username@ftp.domain.org/ftphome/alice/batch123.mtd

You can also only provide the name of the batch and set the `-g` (or
`--glob-file`) flag to let the script look up the corresponding mtd-file on the
FTP-server. For example:

	$ ./report batch123 --glob

**Pro tip**: If you have a lot of batches to check, this bash one-liner can help you out:

	$ while read -r BATCH; do ./report ${BATCH} --glob; done < list-of-batches.txt

Where the file `list-of-batches.txt` is a text file containing all the batches
you want to check, each one on a seperate line.

After usage, the virtual environment can be simply deactivated via:

    $ deactivate
