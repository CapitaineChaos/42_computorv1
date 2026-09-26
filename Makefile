PYTHON      ?= python3
VENV        := .venv
VENV_PYTHON := $(VENV)/bin/python
STAMP       := $(VENV)/.installed
EQ          ?=

PY = $(shell [ -x $(VENV_PYTHON) ] && echo $(VENV_PYTHON) || echo $(PYTHON))

.DEFAULT_GOAL := help
.PHONY: help venv run test lint format clean fclean re

help:
	@grep -E '^[a-z]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

venv: $(STAMP)

$(STAMP): requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -q -r requirements-dev.txt
	@touch $@

run:
	@$(PY) ./computor $(if $(EQ),"$(EQ)")

test:
	$(PY) -m unittest discover -s tests -v

lint: venv
	$(VENV_PYTHON) -m ruff check computorv1 tests computor
	$(VENV_PYTHON) -m ruff format --check computorv1 tests computor

format: venv
	$(VENV_PYTHON) -m ruff format computorv1 tests computor

clean:
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@rm -rf .ruff_cache .coverage

fclean: clean
	@rm -rf $(VENV)

re: fclean venv
