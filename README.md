# InspectionPro

InspectionPro is a web application for managing building inspections, recording structural elements and defects, and preparing inspection reports. The project uses a React/TypeScript frontend, a Django REST Framework API, PostgreSQL, Redis, and Celery.

## Requirements

For the recommended local development setup, install:

- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2 (`docker compose`)

You do **not** need to install Python, Node.js, PostgreSQL, or Redis on your computer for this setup. Docker builds the backend and frontend images and starts the database and Redis services.

The Compose setup uses these local ports:

| Service | Address |
| --- | --- |
| Frontend | <http://localhost:5173> |
| Backend API | <http://localhost:8000/api/> |
| API documentation | <http://localhost:8000/api/docs/> |
| Django admin | <http://localhost:8000/admin/> |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Make sure these ports are available, or update the port mappings in `docker-compose.yml`.

## Clone the repository

Replace `<repository-url>` with the clone URL provided by your Git hosting service:

```bash
git clone <repository-url>
cd InspectionPro
```

## Configure the local environment

Create the local environment file from the checked-in example:

```bash
cp .env.example .env
```

The example values are intended for local development. Before exposing the app beyond your machine, set a unique `DJANGO_SECRET_KEY` and secure database credentials in `.env`. The `.env` file is ignored by Git and should never be committed.

## Install dependencies and launch

Build the images and start the full stack:

```bash
docker compose up --build
```

The first build downloads the base images and installs the Python and Node dependencies, so it can take a few minutes. On startup, the backend applies database migrations automatically. Keep this terminal open to see service logs; press `Ctrl+C` to stop the stack.

To run the services in the background instead:

```bash
docker compose up --build -d
```

Then view logs with:

```bash
docker compose logs -f
```

Open <http://localhost:5173> to use the frontend. The Vite development server proxies `/api` requests to the backend container.

## Optional: load demo data

To populate the database with sample inspection records and local test accounts, run:

```bash
docker compose exec backend python manage.py seed_demo_data
```

The command can be run again to refresh the demo records. It creates these accounts, all with the local-only password `Password123!`:

| Role | Email |
| --- | --- |
| Administrator | `admin@example.com` |
| Manager | `manager@example.com` |
| Engineer | `engineer@example.com` |
| Expert | `expert@example.com` |
| Client | `client@example.com` |

Do not use the demo accounts or password in a deployed environment.

## Everyday development

- Frontend and backend source folders are mounted into their containers. Most code changes are picked up automatically; restart the affected service if they are not.
- After changing Python dependencies in `backend/requirements.txt` or Node dependencies in `frontend/package.json`, rebuild the relevant image:

  ```bash
  docker compose up --build
  ```

- Apply or inspect backend migrations manually if needed:

  ```bash
  docker compose exec backend python manage.py migrate
  docker compose exec backend python manage.py showmigrations
  ```

- Run backend tests:

  ```bash
  docker compose exec backend python manage.py test
  ```

- Build-check the frontend:

  ```bash
  docker compose exec frontend npm run build
  ```

## Stop the app and manage local data

Stop and remove the containers while keeping the PostgreSQL data volume:

```bash
docker compose down
```

Start them again with `docker compose up`. To **also permanently delete** the local database volume and all database data, use:

```bash
docker compose down -v
```

## Troubleshooting

- If Compose reports that `.env` is missing, run `cp .env.example .env` from the repository root.
- If a port is already in use, stop the other service or change its host-side port in `docker-compose.yml`.
- If a service fails during startup, inspect its logs with `docker compose logs -f backend` (or replace `backend` with `frontend`, `postgres`, `redis`, or `celery`).
- If dependencies or container configuration changed, retry with `docker compose up --build`.

For the domain modules and design overview, see [docs/architecture.md](docs/architecture.md).
