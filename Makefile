.PHONY: build
build:
	rm -rf dist/
	python -m build
	pip install dist/*.whl

coverage:
	coverage run -m pytest
	coverage html
	open htmlcov/index.html

format:
	ruff . --fix --ignore E501 --per-file-ignores="__init__.py:F401"
	black .
