.PHONY: ci install lint test

ci: install test

install:
	pip install -r requirements.txt

lint:
	pep8 --format=pylint src test

test:
	pytest

start-db:
	redis-server /usr/local/etc/redis.conf