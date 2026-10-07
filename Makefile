VENV    := .venv
PYTHON  := $(VENV)/bin/python
RUFF    := $(VENV)/bin/ruff
SRC     := computor computorv1 tests

.DEFAULT_GOAL := help
.PHONY: help venv run test provisoire lint format clean fclean re

help:
	@grep -E '^[a-z]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

venv: $(RUFF)

$(RUFF): requirements.txt
	rm -rf $(VENV)
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q --disable-pip-version-check -r requirements.txt
	@touch $@

# `make run "3 * X = 0"`: make reads the quoted equation as a goal, or as an assignment
# when the text before `=` has no space (`3x = 0` gives MAKEOVERRIDES `3x=0`); it is
# glued back from either, and the extra goals do nothing
ifeq (run,$(firstword $(MAKECMDGOALS)))
ARG     := $(subst \_, ,$(firstword $(subst \ ,\_,$(MAKEOVERRIDES))))
ARG     := $(or $(ARG),$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
.DEFAULT: ; @:
endif

run: venv
	@$(PYTHON) ./computor $(if $(ARG),"$(ARG)") || [ $$? -eq 130 ]

# `make test T=saisie` runs tests/test_saisie.py alone, `make test` runs them all
test: venv
	$(PYTHON) -m unittest discover -s tests -p 'test_$(or $(T),*).py' -v

# input tests only, mismatches only, while the parser is being written
provisoire: venv
	@$(PYTHON) tests/provisoire.py

lint: venv
	$(RUFF) check --no-cache $(SRC)

format: venv
	$(RUFF) check --no-cache --fix-only $(SRC)
	$(RUFF) format --no-cache $(SRC)

clean:
	rm -rf computorv1/__pycache__ tests/__pycache__ .ruff_cache

fclean: clean
	rm -rf $(VENV)

re: fclean venv
