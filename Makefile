env ?= local

PROJECT_local = kucode-local
PROJECT_staging = kucode-staging
PROJECT_production = kucode-prod

PROJECT_NAME = $(or $(PROJECT_$(env)),kucode-$(env))
COMPOSE = docker compose -p $(PROJECT_NAME) -f $(env).yml

run:
	$(COMPOSE) up --build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

dev:
	$(MAKE) run env=local

staging:
	$(MAKE) run env=staging

prod:
	$(MAKE) run env=production

migrate:
	$(COMPOSE) exec backend sh -c "python manage.py migrate $(target)"

show_migrate:
	$(COMPOSE) exec backend sh -c "python manage.py showmigrations"

start_app:
	$(COMPOSE) exec backend sh -c "python manage.py startapp $(target)"

makemigrations:
	$(COMPOSE) exec backend sh -c "python manage.py makemigrations"

test:
	$(COMPOSE) exec backend sh -c "python manage.py test"

flake:
	$(COMPOSE) exec backend sh -c "flake8"

createsuperuser:
	$(COMPOSE) exec backend sh -c "python manage.py createsuperuser"
