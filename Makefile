REQ	= requirments.txt
program = Fly-in.py

$(REQ):
	python3 -m pip install pipreqs
	pipreqs .

install: $(REQ)
	python3 -m pip install -r requirements.txt

run:
	python3 program

debug:
	python3 -m pdb program

# need to understand the clean cmd more
clean:
	@echo "Cleaning up temporary files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf .venv
	@echo "Cleanup complete."

lint:
	@echo "\n----Running flake8:----"
	python3 -m flake8 .
	@echo "\n----Running mypy:----"
	# need to understand this flags
	python3 -m mypy .  --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "\n----Running flake8----"
	python3 -m flake8 .
	@echo "\n----Running mypy in strict mode----"
	python3 -m mypy . --strict

.PHONY: install run debug clean lint lint-strict
