PORT ?= 8000
CMD = python manage.py

.PHONY: help
help:
	@echo "Makefile targets:"
	@echo "  runserver PORT=port  - Run the application"
	@echo "  migrate              - Apply database migration"
	@echo "  makemigrations       - Check model changes"
	@echo "  test                 - Run the unit tests"


.PHONY: makemigrations
makemigrations:
	$(CMD) makemigrations

.PHONY: migrate
migrate:
	$(CMD) migrate

.PHONY: test
test:
	$(CMD) test

.PHONY: runserver
runserver: migrate
	$(CMD) runserver 0.0.0.0:${PORT}

