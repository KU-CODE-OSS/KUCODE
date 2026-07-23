# KUCODE (KU COmmunity of DEvelopers)


# Requirements
python >= 3.6  
Node.js >= 18.0  
docker  
docker-compose  

## plugins in vscode
TypeScript Vue Plugin (Volar)   
Vue Language Features (Volar)  
prettier  
Auto Rename Tag  
Auto Close Tag  
Vetur  


---

## Technologies Used

- Docker
- Django
- Postgres
- Vue.js
- Nginx
- Gunicorn

## Features

- Complete setup for Docker, Django, Postgres, Vue.js, and Nginx.
- Accelerated development process.

---



## Setup and Usage

### Setting up environment files

The project uses two kinds of env files:

- `.env`: shared values such as public IP, API keys, OAuth keys, Firebase keys, and sync URLs.
- `.envs/<environment>/*.env`: service/runtime values such as Django settings, database settings, and pgAdmin login.

```bash
# .env
PUBLIC_IP=  # Place to write the IP address (exclude 'http://')
FASTAPI_PORT=5000
VITE_API_BASE=/api
VUE_APP_API_URL=http://${PUBLIC_IP}:8000/api
CORS_ALLOWED_ORIGIN=http://${PUBLIC_IP}

OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
KOREAUNIV_OPENAPI_CLIENT_ID=
KOREAUNIV_OPENAPI_CLIENT_SECRET=
KOREAUNIV_OPENAPI_TOKEN=

STUDENT_SYNC_URL=
REPO_SYNC_URL=
REPO_COMMIT_SYNC_URL=
REPO_ISSUE_SYNC_URL=
REPO_PR_SYNC_URL=
REPO_CONTRIBUTOR_SYNC_URL=
COURSE_{NAME}_SYNC=
```

In this setup, if you are running the environment locally, you can use localhost or 127.0.0.1 as the PUBLIC_IP. However, in a cloud environment, you should specify the public IP address.

For examples, refer to `.env_example` and the `.env.sample` files under `.envs/`.

Current environment policy:

- Keep shared API keys/secrets in root `.env` for now.
- Keep service-specific values in `.envs/.local`, `.envs/.staging`, and `.envs/.production`.
- Local, staging, and production may share DB credentials and `SECRET_KEY` for now.
- Docker Compose project names and Docker volumes separate the actual containers/data.
- Commit only `.env_example` and `.env.sample` files. Do not commit real `.env` files.

Before running staging or production for the first time, create real files from the samples:

```bash
cp .envs/.staging/django.env.sample .envs/.staging/django.env
cp .envs/.staging/postgres.env.sample .envs/.staging/postgres.env
cp .envs/.production/django.env.sample .envs/.production/django.env
cp .envs/.production/postgres.env.sample .envs/.production/postgres.env
```

### Running Locally

To run the project locally for development, you can use the provided `local.yml` Docker Compose file along with the `Makefile`.

```bash
make run
```

Equivalent explicit command:

```bash
docker compose -p kucode-local -f local.yml up --build
```

| Container  | Service | Host Port | Docker Port |
| ---------- | ------- | --------- | ----------- |
| backend    | django  | 8000      | 8000        |
| frontend   | vuejs   | 5173      | 5173        |
| db         | db      |           | 5432        |
| pgadmin    | pgadmin | 9000      | 80          |
| nginx      | nginx   | 8080/8443 | 80/443      |

NOTE: `nginx` container shows ports for `http/https` entrypoints respectively.

### Running in Staging

Staging is production-like and should usually be deployed from the `dev_all` branch.

```bash
make staging
```

Equivalent explicit command:

```bash
docker compose -p kucode-staging -f staging.yml up --build
```

| Container | Service | Host Port | Docker Port |
| --------- | ------- | --------- | ----------- |
| backend   | django  |           | 8000        |
| db        | db      |           | 5432        |
| nginx     | nginx   | 8081      | 80          |

### Running in Production

To run the project in a production environment, use the provided `production.yml` Docker Compose file along with the `Makefile`.

```bash
make prod
```

Equivalent explicit command:

```bash
docker compose -p kucode-prod -f production.yml up --build
```

| Container  | Service | Host Port | Docker Port |
| ---------- | ------- | --------- | ----------- |
| backend    | django  |           | 8000        |
| db         | db      |           | 5432        |
| nginx      | nginx   | 80        | 80          |

Important: always run Compose with the correct project name (`kucode-local`, `kucode-staging`, or `kucode-prod`). This prevents containers, networks, and volumes from colliding on the same machine.

Recommended branch flow:

```text
feature branches -> dev_all -> main
local.yml        -> staging.yml -> production.yml
```

### Useful Makefile Commands

- `make migrate`: Run Django migrations.
- `make makemigrations`: Generate Django migration files.
- `make test`: Run Django tests.
- `make flake`: Run Flake8 for linting.
- `make staging`: Run the production-like staging stack.
- `make prod`: Run the production stack.

### Health Check Endpoint

In the Django backend, an API endpoint `/api/healthcheck` has already been implemented. This endpoint is designed to provide a quick health status check of the backend. When accessed, it returns a `200 OK` response, indicating that the backend is up and running properly.

This health check endpoint can be useful for monitoring the status of the backend application, especially in production environments where it's essential to ensure the availability and reliability of the services.

### Endpoints

- `/`: Vue.js with Vite example app.
<!-- - `/admin`: Django admin panel. To access, you need to create a superuser using `make createsuperuser`. -->
- `/api`: Django API. Includes `/api/healthcheck` endpoint.

## Make crawling sh and run
To crawl only updated repos of students in recent semester and course order, run:
```
nohup ./crawling.sh > crawling.log 2>&1 &
```

To crawl every repos of students in recent semester and course order, run:
```
nohup ./crawling.sh --scope=all > crawling.log 2>&1 &
```

To crawl students in default order, run:
```
nohup ./crawling.sh --student-order=default > crawling.log 2>&1 &
```

To crawl every repos of students in default order, run:
```
nohup ./crawling.sh --scope=all --student-order=default > crawling.log 2>&1 &
```

## DB backup command
In dev_db container, execute command below to create backup sql file.
```
pg_dump -U postgres -d django_project_db -b -v -f /home/backup_db_[yyyymmdd]_[hhmm].sql
```
In local terminal, outside the docker container, execute command below to copy the backup file from the container to local directory.
```
sudo docker cp dev_db:/home/backup_db_[날짜]_[시간].sql /home/kucode/backup/DB/
```

## DB import from backup
To import a backup SQL file into an environment, copy the SQL file into that environment's DB container, reset the new DB schema, then run `psql`.

Example for local:
```
docker compose -p kucode-local -f local.yml cp /home/kucode/backup/DB/backup_db_[yyyymmdd]_[hhmm].sql db:/tmp/backup.sql
docker compose -p kucode-local -f local.yml exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"'
docker compose -p kucode-local -f local.yml exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/backup.sql'
docker compose -p kucode-local -f local.yml restart backend
```

For staging or production, replace the project name and compose file:
```
kucode-local    local.yml
kucode-staging  staging.yml
kucode-prod     production.yml
```

Do not use `down -v` or remove Docker volumes unless you intentionally want to delete database data.


## 기여 가이드라인
**이 프로젝트에 기여를 하고자 한다면 
[기여 가이드라인](.github/CONTRIBUTING.md) 을 읽어보시기를 바랍니다.**
