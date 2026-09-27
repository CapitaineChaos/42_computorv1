SHM     := /dev/shm/computorv1
VENV    := $(SHM)/.venv
SRC     := computor computorv1 tests
RUFF    := $(VENV)/bin/ruff
EQ      ?=

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
	$(VENV)/bin/pip install -q -r requirements.txt
	@touch $@

run: sync
	@cd $(SHM) && python3 ./computor $(if $(EQ),"$(EQ)")

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
