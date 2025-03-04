init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	python -m pre_commit install

reqs::
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

upgrade::
	python -m piptools compile --upgrade requirements/requirements.in
	python -m piptools sync requirements/requirements.txt

black:
	black bin

black-check:
	black --check bin

flake8:
	flake8 bin

isort:
	isort --profile black bin

lint: black-check flake8
