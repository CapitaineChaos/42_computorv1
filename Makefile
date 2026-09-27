SHM     := /dev/shm/computorv1
VENV    := $(SHM)/.venv
SRC     := computor computorv1 tests
RUFF    := $(VENV)/bin/ruff

.DEFAULT_GOAL := help
.PHONY: help sync venv run test lint format clean fclean re

help:
	@grep -E '^[a-z]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

sync:
	@mkdir -p $(SHM)
	@rsync -a --delete --exclude __pycache__ $(SRC) $(SHM)/

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

run: sync
	@cd $(SHM) && python3 ./computor $(if $(ARG),"$(ARG)") || [ $$? -eq 130 ]

test: sync
	cd $(SHM) && python3 -m unittest discover -s tests -v

lint: venv
	$(RUFF) check --no-cache $(SRC)

format: venv
	$(RUFF) check --no-cache --fix-only $(SRC)
	$(RUFF) format --no-cache $(SRC)

clean:
	rm -rf $(SHM)/*/__pycache__

fclean:
	rm -rf $(SHM)

re: fclean sync venv
