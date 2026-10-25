VENV    := .venv
RUFF    := $(VENV)/bin/ruff
SRC     := computor computorv1

export UV_PYTHON_INSTALL_DIR ?= /tmp/uv/python
export UV_CACHE_DIR ?= /tmp/uv/cache

.DEFAULT_GOAL := help
.PHONY: help venv lint format clean fclean re

help:
	@grep -E '^[a-z_]+:' Makefile | cut -d: -f1 | tr '\n' ' '
	@echo

venv:
	@$(VENV)/bin/python -c "" 2>/dev/null || rm -f $(RUFF)
	@$(MAKE) -s --no-print-directory $(RUFF)

$(RUFF): requirements.txt
	rm -rf $(VENV)
	uv venv --quiet --seed --python 3.14 $(VENV)
	$(VENV)/bin/pip install -q --disable-pip-version-check -r requirements.txt
	@touch $@

lint: venv
	$(RUFF) check --no-cache $(SRC)

format: venv
	$(RUFF) check --no-cache --fix-only $(SRC)
	$(RUFF) format --no-cache $(SRC)

clean:
	rm -rf computorv1/__pycache__ .ruff_cache

fclean: clean
	rm -rf $(VENV)

re: fclean venv
