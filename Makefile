test:
	python3 -m pytest
	python3 -m coverage report

lint:
	isort --check --profile black -t py311 -l 79 src
	mypy --install-types --non-interactive
	flake8 src/freva_stats_service --count --max-complexity=8 --ignore=F405,W503 --max-line-length=88 --statistics --show-source
