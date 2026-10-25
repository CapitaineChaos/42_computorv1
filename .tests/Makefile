PYTHON  := $(abspath ../.venv/bin/python)
RUFF    := $(abspath ../.venv/bin/ruff)

.DEFAULT_GOAL := help
.PHONY: help venv test test_solutions test_common test_display lint format clean

help:
	@grep -E '^[a-z_]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

venv:
	@$(MAKE) -s --no-print-directory -C .. venv

test: venv
	$(PYTHON) -m unittest discover -s . -p 'test_$(or $(T),*).py' -v

test_solutions: venv
	@$(PYTHON) -m unittest test_solutions

ifneq (,$(filter test_common test_display,$(firstword $(MAKECMDGOALS))))
G       := $(or $(G),$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
.DEFAULT: ; @:
endif

test_common: venv
	@$(PYTHON) report.py common $(G)

test_display: venv
	@$(PYTHON) report.py display $(G)

lint: venv
	$(RUFF) check --no-cache .

format: venv
	$(RUFF) check --no-cache --fix-only .
	$(RUFF) format --no-cache .

clean:
	rm -rf __pycache__
