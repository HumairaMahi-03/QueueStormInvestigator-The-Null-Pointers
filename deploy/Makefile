# deploy/Makefile
.PHONY: build run stop test clean logs shell

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

test:
	docker-compose --profile test run --rm test-runner

logs:
	docker-compose logs -f

shell:
	docker-compose exec ticket-triage /bin/bash

clean:
	docker-compose down -v
	docker system prune -f