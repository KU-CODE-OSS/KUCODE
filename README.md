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
| nginx     | nginx   | 8081/8444 | 80/443      |

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
| nginx      | nginx   | 80/443    | 80/443      |

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

## E-Profile 저장소 기능 조회

E-Profile → 나의 프로젝트 → Repository 이름을 누르면 `frontend/src/views/EProfileComponents/RepoDetailModal.vue`가 열립니다. 이 모달에 전달되는 `repo.id`로 다음 API를 호출할 수 있습니다.

| GET 요청 | 조회 범위 |
|---|---|
| `/api/repo/features/?repo_id=<repo.id>` | 해당 프로젝트의 분석된 코드블록과 기능 목록 |
| `/api/repo/features/?repo_id=<repo.id>&scope=contributed` | 로그인한 학생이 해당 프로젝트에 기여한 코드블록 |
| `/api/repo/features/` | 로그인한 학생의 분석된 프로젝트 전체 기여 |
| `/api/repo/features/?student_id=<student.id>` | 관리자가 지정한 학생의 분석된 프로젝트 전체 기여 |
| `/api/repo/features/?repo_id=<repo.id>&student_id=<student.id>` | 지정한 학생의 해당 프로젝트 기여 |

다른 E-Profile 요청과 같은 Firebase ID 토큰을 `Authorization: Bearer <token>`으로 보내세요. 학생은 본인 데이터와 소유 또는 기여가 확인된 저장소를 조회할 수 있습니다. 관리자는 저장소 전체나 지정 학생의 기여를 조회할 수 있습니다. 팀 저장소가 대표 코드베이스로 묶인 경우 근거 링크는 분석 시점의 대표 저장소와 커밋을 가리킵니다.

기능은 `features`, 원본 파일·행 범위·코드 링크는 `features[].evidence`에 있습니다. `summary`에는 배정·미배정 건수가 있고, `unassigned`에는 사전에 배정되지 않은 코드블록이 있습니다. `dictionary` 기본값은 `spec_hierarchical`이고 `spec_umap_hdbscan`, `code_hierarchical`, `code_umap_hdbscan`도 선택할 수 있습니다. `limit`은 기본 50, 최대 100이며 `offset`으로 기능 목록을 넘깁니다. 기능 사전의 상태와 각 항목의 검토 표시도 응답에 포함됩니다.

`404 repository_not_analyzed`는 해당 레포의 분석 결과가 아직 없다는 뜻입니다. 분석 스냅샷을 연결하지 않았거나 읽을 수 없으면 `503 snapshot_unavailable`을 반환합니다.

### 스테이징 데이터 연결

분석 파이프라인의 `build_snapshot.py`가 만드는 `feature-api-snapshot-v1` JSON을 배포 서버의 접근 제한 폴더에 준비합니다. 컨테이너의 Django 실행 계정이 파일을 읽을 수 있어야 합니다. 스테이징 스택이 실행 중이면 아래 명령으로 백엔드에 읽기 전용 마운트를 적용합니다.

```bash
export FEATURE_LOOKUP_SNAPSHOT_HOST=/path/to/private/snapshot.json
docker compose -p kucode-staging -f staging.yml \
  -f compose/staging/feature-lookup.yml up -d --build --no-deps backend
```

Django는 `FEATURE_LOOKUP_SNAPSHOT`이 가리키는 파일을 프로세스에서 읽습니다. 새 스냅샷으로 교체할 때는 마운트를 포함한 위 Compose 구성으로 백엔드 컨테이너를 다시 생성합니다. 스냅샷, 벡터 배열, 실험 산출물, SSH 설정과 자격증명은 Git 및 이미지 밖의 서버 파일로 관리합니다.

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

### Repository summary generation

Repository summary generation uses the repository data saved in the database together with live GitHub context such as the file tree, README, workflows, and configuration files. It requires `OPENAI_API_KEY` in the root `.env` file and a running Django backend.

Summary-only commands exit after the summary operation; they do not run the normal continuous GitHub crawling loop.

#### Live pricing test without saving

Run real summary API calls for a sample of 1 to 500 repositories and report token usage and estimated cost without changing `Repository.summary`:

```bash
./crawling.sh --summary-test=100
```

Use a different deterministic sample when required:

```bash
./crawling.sh --summary-test=100 --summary-seed=12345
```

Review `actual_cost_usd` and `projected_eligible_cost_usd` in the JSON response.

#### Save a limited summary refresh batch

Refresh and save up to 1 to 500 repositories that require summary work:

```bash
./crawling.sh --summary-update=100
```

Eligible repositories include:

- repositories with no summary;
- legacy summaries without a generation fingerprint;
- summaries made stale by repository data, model, or prompt-version changes; and
- repositories whose previous summary attempt failed.

The backend prioritizes missing, legacy, stale, and previously failed summaries in that order. A failed attempt does not replace an existing saved summary; a repository with no successful summary remains `NULL` and can be retried.

#### Save all required summary updates

Process every currently eligible repository in batches of up to 500:

```bash
./crawling.sh --summary-update=all
```

Each eligible repository is attempted once during that execution. Successful batches are saved immediately. Run the same command again to retry repositories that failed.

To run the full refresh in the background and follow its output:

```bash
nohup ./crawling.sh --summary-update=all > summary_update.log 2>&1 &
tail -f summary_update.log
```

The output includes per-batch saved/failed counts, token usage, and estimated USD cost.

#### Optional summary refresh during continuous crawling

Set `SUMMARY_BATCH_SIZE` in `.env` to a value from 1 to 500 to run one summary refresh batch after each normal crawling cycle:

```bash
SUMMARY_BATCH_SIZE=100
```

Leave it unset or set it to `0` to keep summary generation separate from crawling.

## Scoring commands

Run these Django management commands inside the backend container.

### Score one course-semester

```bash
python manage.py score_course --course-id COSE341-01 --year 2026 --semester 1
```

Recalculates one course's scoring records and updates the affected students' E-Profile aptitude scores.

### Score all or filtered courses

```bash
python manage.py score_all_courses
python manage.py score_all_courses --year 2026 --semester 1
python manage.py score_all_courses --course-id COSE341-01
```

Recalculates every matching course and updates the affected students' E-Profile aptitude scores.

### Rebuild E-Profile aptitude scores

```bash
python manage.py rebuild_student_aptitudes
python manage.py rebuild_student_aptitudes --formula-version prototype-v1
```

Rebuilds E-Profile aptitude aggregates from the currently saved canonical scoring records without rescoring courses.

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
