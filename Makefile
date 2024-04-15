env ?= local

run:
	docker compose -f ${env}.yml up --build

migrate:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py migrate $(target)"

show_migrate:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py showmigrations"

start_app:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py startapp $(target)"

makemigrations:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py makemigrations"

test:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py test"

flake:
	docker compose -f ${env}.yml exec backend sh -c "flake8"

createsuperuser:
	docker compose -f ${env}.yml exec backend sh -c "python manage.py createsuperuser"
