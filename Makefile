PROGRAM = fly_in.py
CONFIG = maps/easy/01_linear_path.txt
REQ = requirements.txt

.PHONY: install run debug clean lint lint-strict requirements

install:
	pip install -r $(REQ)

run:
	@for map in $$(find maps -name "*.txt"); do \
		echo "Running on $$map"; \
		python3 $(PROGRAM) $$map; \
	done

debug:
	python3 -m pdb $(PROGRAM) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 . --exclude=venv
	mypy . --exclude venv/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
