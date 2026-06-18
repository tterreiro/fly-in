VENV := fly_in_venv
PYTHON := maze_venv/bin/python3
PIP := maze_venv/bin/pip3
MAIN := fly_in.py
CONFIG := config.txt

install: v_env

v_env:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	python3 -m wheel unpack ./lib/mlx-2.2-py3-ubuntu-any.whl
	mv ./mlx-2.2/mlx ./lib
	rm -fr ./mlx-2.2


run: install
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "_pycache_" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf $(VENV)
	rm -rf lib/mlx

lint:
	flake8 . --exclude lib,venv
	mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . --exclude lib,venv
	mypy src/ --strict --allow-untyped-calls --ignore-missing-imports

.PHONY: install run debug clean lint lint-strict build
