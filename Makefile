# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dmota-ri <dmota-ri@student.42lisboa.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/10 16:50:27 by dmota-ri          #+#    #+#              #
#    Updated: 2026/05/14 19:49:00 by dmota-ri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = Fly-in

DEPENDENCIES = pydantic mypy flake8 pygame

MAIN = main

# MAP_FILE = maps/easy/01_linear_path.txt
# MAP_FILE = maps/easy/02_simple_fork.txt
# MAP_FILE = maps/easy/03_basic_capacity.txt

# MAP_FILE = maps/easy/02_simple_fork_copy.txt

# MAP_FILE = maps/medium/01_dead_end_trap.txt
# MAP_FILE = maps/medium/02_circular_loop.txt
# MAP_FILE = maps/medium/03_priority_puzzle.txt

# MAP_FILE = maps/hard/01_maze_nightmare.txt
# MAP_FILE = maps/hard/02_capacity_hell.txt
# MAP_FILE = maps/hard/03_ultimate_challenge.txt

MAP_FILE = maps/challenger/01_the_impossible_dream.txt

OBJ = **.py *.py

VENV = .venv/

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m

RM = rm -fr


run:
	$(PYTHON) $(MAIN) $(MAP_FILE)

test_all:
	@echo Easy
	@echo "linear path"
	$(PYTHON) $(MAIN) maps/easy/01_linear_path.txt
	@echo "simple fork"
	$(PYTHON) $(MAIN) maps/easy/02_simple_fork.txt
	@echo "basic capacity"
	$(PYTHON) $(MAIN) maps/easy/03_basic_capacity.txt

	$(PYTHON) $(MAIN) maps/easy/02_simple_fork_copy.txt
	$(PYTHON) $(MAIN) maps/easy/03_basic_capacity_copy.txt

	@echo
	@echo Medium
	@echo "dead end trap"
	$(PYTHON) $(MAIN) maps/medium/01_dead_end_trap.txt
	@echo "circular loop"
	$(PYTHON) $(MAIN) maps/medium/02_circular_loop.txt
	@echo "priority puzzle"
	$(PYTHON) $(MAIN) maps/medium/03_priority_puzzle.txt

	@echo
	@echo Hard
	@echo "maze nightmare"
	$(PYTHON) $(MAIN) maps/hard/01_maze_nightmare.txt  # map Error??
	@echo "capacity hell"
	$(PYTHON) $(MAIN) maps/hard/02_capacity_hell.txt
	@echo "ultimate challenge"
	$(PYTHON) $(MAIN) maps/hard/03_ultimate_challenge.txt

	@echo
	@echo Challenger
	@echo "the impossible dream"
	$(PYTHON) $(MAIN) maps/challenger/01_the_impossible_dream.txt

	@echo
	@echo "All Tests Done"

debug:
	$(DEBUGGER) $(MAIN).py $(MAP_FILE)

.ONESHELL:

install: $(VENV)
	source $(VENV)bin/activate
	pip install $(DEPENDENCIES)
	export PYGAME_HIDE_SUPPORT_PROMPT=1

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
