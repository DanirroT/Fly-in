NAME = Fly-in

DEPENDENCIES = pydantic mypy flake8

MAIN = input
# MAIN = main

OBJ = **.py

#BONUS = ft_lists_1_bonus.c ft_lists_2_bonus.c

#B_OBJ = $(BONUS:.c=.o)

INC = codexion.h

DEBUGGER = $(PYTHON) -m pdb
PYTHON = python3 -m

RM = rm -fr

install:
	$(PYTHON) -m venv .venv
	source .venv/bin/activate
	pip install $(DEPENDENCIES)

# install:
# 	curl -LsSf https://astral.sh/uv/install.sh | sh
# 	uv venv
# 	source .venv/bin/activate
# 	uv sync

debug:
	$(DEBUGGER) $(MAIN)

run:
	$(PYTHON) $(MAIN)

clean:
	$(RM) ./__pycache__/ ./.mypy_cache/
	$(RM) ./src/__pycache__/ ./src/.mypy_cache/

lint:
	@flake8 $(OBJ) || true
	@mypy $(OBJ) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || true

lint-strict:
	@flake8 $(OBJ) || true
	@mypy $(OBJ) --strict || true
