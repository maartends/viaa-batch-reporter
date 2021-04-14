# batch-reporter
SHELL:=/bin/bash

.ONESHELL:
.PHONY: install-req make-help help lint venv-activate

init-venv:
	@echo "[INIT-VENV]: Init virtual environment..."
	python3 -m venv .

venv-activate:
	@echo "[VENV-ACTIVATE]: Init virtual environment..."
	source bin/activate

make-help:
	@echo "Usage: $ make <target>"
	@echo "	> help      : show script options"
	@echo "	> install-req"
	@echo "	> lint"
	@echo "	> install"

install-req:
	@echo "[INSTALL-REQ]: Install requirements..."
	source bin/activate; \
		pip install wheel; \
		pip install -r requirements.txt

help:
	@echo "[HELP]: show script options"
	source bin/activate; \
		./report -h

lint:
	@echo "[LINT]: Run Flake8 linter on code syntax"
	source bin/activate; \
		python -m flake8 --ignore E221,E251 run.py

mv-config:
	@echo "[MV-CONFIG]: Rename 'config.yml.example' to 'config.yml'..."
	cp config.yml.example config.yml

all: init-venv install-req mv-config
	@echo "***********************************************"
	@echo "* Succes: see README.md for more information. *"
	@echo "*         or do 'make help'                   *"
	@echo "***********************************************"

install: all
