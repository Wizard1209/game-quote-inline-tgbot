polling:
	python src/app.py -p quotes.json

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

r: down up

.PHONY: polling build up down logs r
