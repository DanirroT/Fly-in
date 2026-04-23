# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dmota-ri <dmota-ri@student.42lisboa.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/10 16:50:27 by dmota-ri          #+#    #+#              #
#    Updated: 2026/04/23 14:57:16 by dmota-ri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = Fly-in

DEPENDENCIES = pydantic mypy flake8 pygame

MAIN = main

# MAP_FILE = maps/easy/01_linear_path.txt
# MAP_FILE = maps/easy/02_simple_fork.txt
# MAP_FILE = maps/easy/03_basic_capacity.txt
MAP_FILE = maps/hard/01_maze_nightmare.txt
# MAP_FILE = maps/challenger/01_the_impossible_dream.txt

OBJ = **.py *.py

VENV = .venv

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m

RM = rm -fr

.ONESHELL:

run:
	$(PYTHON) $(MAIN) $(MAP_FILE)

debug:
	$(DEBUGGER) $(MAIN).py $(MAP_FILE)

install: $(VENV)
	source $(VENV)/bin/activate
	pip install $(DEPENDENCIES)

$(VENV):
	$(PYTHON) venv $(VENV)

# install:
# 	curl -LsSf https://astral.sh/uv/install.sh | sh
# 	uv venv
# 	source .venv/bin/activate
# 	uv sync

clean:
	$(RM) ./__pycache__/ ./.mypy_cache/
	$(RM) ./src/__pycache__/ ./src/.mypy_cache/

lint:
	@flake8 $(OBJ) || true
	@mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@flake8 $(OBJ) || true
	@$(PYTHON) mypy --strict $(OBJ) || true
# 	@mypy --strict $(OBJ) || true
