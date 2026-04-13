NAME = Fly-in

DEPENDENCIES = pydantic mypy flake8

MAIN = input
# MAIN = main

# MAP_FILE = maps/easy/01_linear_path.txt
MAP_FILE = maps/easy/02*
# MAP_FILE = maps/easy/03*

OBJ = **.py

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m

RM = rm -fr

install:
	$(PYTHON) venv .venv
	source .venv/bin/activate
	pip install $(DEPENDENCIES)

# install:
# 	curl -LsSf https://astral.sh/uv/install.sh | sh
# 	uv venv
# 	source .venv/bin/activate
# 	uv sync

debug:
	$(DEBUGGER) $(MAIN) $(MAP_FILE)

run:
	$(PYTHON) $(MAIN) $(MAP_FILE)

clean:
	$(RM) ./__pycache__/ ./.mypy_cache/
	$(RM) ./src/__pycache__/ ./src/.mypy_cache/

lint:
	@flake8 $(OBJ) || true
	@mypy $(OBJ) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || true

lint-strict:
	@flake8 $(OBJ) || true
	@mypy $(OBJ) --strict || true
