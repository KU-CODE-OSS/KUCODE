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

### Setting up the .env file

To get started, you need to create a .env file in the root directory of the project. Then, you must populate it following this format:

```bash
# .env
PUBLIC_IP=  # Place to write the IP address (exclude 'http://')
VUE_APP_API_URL=http://${PUBLIC_IP}:8000/api
CORS_ALLOWED_ORIGIN=http://${PUBLIC_IP}
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
KOREAUNIV_OPENAPI_CLIENT_ID=
KOREAUNIV_OPENAPI_CLIENT_SECRET=

STUDENT_SYNC_URL=
REPO_SYNC_URL=
REPO_COMMIT_SYNC_URL=
REPO_ISSUE_SYNC_URL=
REPO_PR_SYNC_URL=
REPO_CONTRIBUTOR_SYNC_URL=
COURSE_{NAME}_SYNC=
```

In this setup, if you are running the environment locally, you can use localhost or 127.0.0.1 as the PUBLIC_IP. However, in a cloud environment, you should specify the public IP address.

For an example, refer to the .env_example file provided in the project.

### Running Locally

To run the project locally for development, you can use the provided `local.yml` Docker Compose file along with the `Makefile`.

```bash
make run
```

| Container  | Service | Host Port | Docker Port |
| ---------- | ------- | --------- | ----------- |
| dev-django | django  | 8000      | 8000        |
| dev-frontend  | vuejs   | 80      | 5173        |
| dev-db     | db      |       | 5432        |
| dev-pg-admin     | pg-admin      | 9000      | 80        |

### Running in Production

To run the project in a production environment, you can use the provided `production.yml` Docker Compose file along with the `Makefile`.
Before running in production, make sure to add the necessary environment settings for each service in the .envs/.production directory. Sample environment files for each service are provided in this directory and need to be configured accordingly.

```bash
make run env=production
```

| Container  | Service | Host Port | Docker Port |
| ---------- | ------- | --------- | ----------- |
| django     | django  |           | 8000        |
| db         | db      |           | 5432        |
| nginx      | nginx   | 80        | 80          |

For a quick check of what it looks like in production you can copy the files in .envs/.local to .envs/.production

### Useful Makefile Commands

- `make migrate`: Run Django migrations.
- `make makemigrations`: Generate Django migration files.
- `make test`: Run Django tests.
- `make flake`: Run Flake8 for linting.

### Health Check Endpoint

In the Django backend, an API endpoint `/api/healthcheck` has already been implemented. This endpoint is designed to provide a quick health status check of the backend. When accessed, it returns a `200 OK` response, indicating that the backend is up and running properly.

This health check endpoint can be useful for monitoring the status of the backend application, especially in production environments where it's essential to ensure the availability and reliability of the services.

### Endpoints

- `/`: Vue.js with Vite example app.
<!-- - `/admin`: Django admin panel. To access, you need to create a superuser using `make createsuperuser`. -->
- `/api`: Django API. Includes `/api/healthcheck` endpoint.

## Make crawling sh and run
```
nohup ./crawling.sh > crawling.log 2>&1 &
```

## 기여 가이드라인
**이 프로젝트에 기여를 하고자 한다면 
[기여 가이드라인](.github/CONTRIBUTING.md) 을 읽어보시기를 바랍니다.**
