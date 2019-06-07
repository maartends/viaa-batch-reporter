# Batch reporting script

Script to report on batches in the archiving backend.

## Prerequisites

- Python 3
- Python 3 virtualenv

Check your Python version with:

    $ python --version

or:

    $ python3 --version

## Installation

- Clone this repository

      $ git clone git@github.com:maartends/viaa-batch-reporter.git

- cd into the cloned directory and create a python virtual environment

      $ python3 -m venv .

    (notice the `.` at the end)

- Activate the virtual environment

      $ source bin/activate

- Install requirements

      $ pip install -r requirements.txt

- Rename `config.yml.example` to `config.yml`

      $ mv config.yml.example config.yml

- Run `help` to check if the installation succeeded

      $ ./report -h

Output should be as below.

## Usage

Output of `$ ./report -h`:

```
usage: batch-reporter [-h] [-m MTD] batch

Report on batches

positional arguments:
  batch              Specify batchname.

optional arguments:
  -h, --help         show this help message and exit
  -m MTD, --mtd MTD  Filepath to mtd (csv) file.
```

Before running, the configuration file `config.yml` should be filled in.

Than run with, for example:

    $ ./report batch123 --mtd /home/alice/batch123.mtd

