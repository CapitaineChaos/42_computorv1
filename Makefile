VENV    := .venv
PYTHON  := $(VENV)/bin/python
RUFF    := $(VENV)/bin/ruff
SRC     := computor computorv1 tests

.DEFAULT_GOAL := help
.PHONY: help venv run test provisoire fuzz lint format clean fclean re

help:
	@grep -E '^[a-z]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

venv: $(RUFF)

$(RUFF): requirements.txt
	rm -rf $(VENV)
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q --disable-pip-version-check -r requirements.txt
	@touch $@

ifeq (run,$(firstword $(MAKECMDGOALS)))
ARG     := $(subst \_, ,$(firstword $(subst \ ,\_,$(MAKEOVERRIDES))))
ARG     := $(or $(ARG),$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
.DEFAULT: ; @:
endif

run: venv
	@$(PYTHON) ./computor $(if $(ARG),"$(ARG)") || [ $$? -eq 130 ]

test: venv
	$(PYTHON) -m unittest discover -s tests -p 'test_$(or $(T),*).py' -v

ifeq (provisoire,$(firstword $(MAKECMDGOALS)))
G       := $(or $(G),$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)))
.DEFAULT: ; @:
endif

provisoire: venv
	@$(PYTHON) tests/provisoire.py $(G)

ifeq (fuzz,$(firstword $(MAKECMDGOALS)))
N       := $(or $(N),$(word 2,$(MAKECMDGOALS)))
.DEFAULT: ; @:
endif

fuzz: venv
	@$(PYTHON) tests/fuzz.py $(if $(N),--count $(N)) $(if $(SEED),--seed $(SEED))

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
