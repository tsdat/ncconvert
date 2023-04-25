build:
	rm -rf dist/
	python -m build
	pip install dist/*.whl

coverage:
	coverage run -m pytest
	coverage html
	open htmlcov/index.html

format:
	ruff . --fix --ignore E501
	black .
