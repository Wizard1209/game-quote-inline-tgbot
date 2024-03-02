polling:
	python quotebot/main.py -p quotes.json

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

pull:
	git pull

r: pull build down up

.PHONY: polling build up down logs r
