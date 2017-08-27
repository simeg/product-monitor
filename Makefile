.PHONY: ci install lint test deploy start-db

ci: install lint test

install:
	pip install -r requirements.txt

lint:
	pep8 --format=pylint src test

test:
	pytest

deploy:
	git push heroku master

start-db:
	redis-server /usr/local/etc/redis.conf
