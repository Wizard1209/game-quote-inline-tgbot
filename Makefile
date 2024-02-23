polling:
	python src/app.py api_key.txt

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

rebuild: down build up

.PHONY: build up down rebuild
