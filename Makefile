

install:
	pip install pygame

run:
	python3 main.py maps/challenger/01_the_impossible_dream.txt

debug:
	pdb3 main.py

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict