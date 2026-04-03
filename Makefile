PROGRAM = fly_in.py
CONFIG = maps/easy/01_linear_path.txt
REQ = requirements.txt

.PHONY: install run debug clean lint lint-strict requirements

install:
	pip install -r $(REQ)

run:
	@(python3 $(PROGRAM) $(CONFIG))

debug:
	python3 -m pdb $(PROGRAM) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
