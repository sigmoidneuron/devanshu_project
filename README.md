# Phone Number Search Monorepo

This repository contains a production-ready backend for a phone-number search product. It ships two Django services that share a single database via the `shared.core` reusable app:

- **API Service** (`services/api`): Public REST API providing prefix listings, similarity-based related-number search, health, readiness, metrics, and OpenAPI docs.
- **Admin Service** (`services/admin`): Authenticated dashboard with HTML pages and JSON endpoints for managing phone numbers, bulk uploads, and credential management.

Both services run on Python 3.11+, expose ASGI-compatible interfaces, and support SQLite (default) or PostgreSQL by configuration.

## Repository layout

```
.
├── docker-compose.yml
├── Makefile
├── nginx/
├── infra/deploy/
├── services/
│   ├── api/
│   └── admin/
├── shared/core/
└── scripts/
```

## Prerequisites

- Python 3.11+
- pip
- Docker & Docker Compose v2
- Node-based frontend (optional; not part of this repo)

## Environment configuration

Copy the provided examples and adjust for your environment.

```bash
cp .env.example .env
cp services/api/.env.example services/api/.env
cp services/admin/.env.example services/admin/.env
```

Key variables:

- `DJANGO_SECRET_KEY`: Unique secret for each service.
- `DJANGO_DEBUG`: `true` in development, `false` in production.
- `DATABASE_ENGINE`: `sqlite` (default) or `postgres`.
- `DATABASE_URL`: Optional DSN (postgres or sqlite) that overrides individual settings.
- `ALLOWED_HOSTS`: Comma-separated hosts each service will trust.
- `CORS_ALLOWLIST`: Origins permitted to call the service (`https://www.example.com` for API, `https://admin.example.com` for admin).
- `RATE_LIMITS_PUBLIC`, `RATE_LIMITS_ADMIN`, `RATE_LIMITS_LOGIN`: Rate limit strings for DRF and `django-ratelimit`.
- `CACHE_DIR`: Directory for the shared file-based cache used by rate limiting.
- `RATELIMIT_CACHE_TABLE`: Database table name for the dedicated rate-limit cache backend.

### Switching to PostgreSQL

Set the following values (or provide a single `DATABASE_URL`):

```
DATABASE_ENGINE=postgres
DATABASE_NAME=phone_numbers
DATABASE_USER=postgres
DATABASE_PASSWORD=<password>
DATABASE_HOST=postgres
DATABASE_PORT=5432
```

Both services will connect to the same PostgreSQL database without code changes.

## Local development quickstart

```bash
# install dependencies
python -m pip install --upgrade pip
pip install -e .

# run migrations once for the shared schema
python services/api/manage.py migrate

# seed with an admin user (admin / ChangeMeNow!2025) and sample numbers
python services/api/manage.py seed

# start both services with autoreload
make dev
```

Services start on:

- API: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8001

## Testing

```bash
make test
```

This runs the pytest suites for both services with SQLite. CI additionally exercises PostgreSQL.

## Database seeding

```bash
make migrate
make seed
```

The seed command creates the default admin credentials (`admin` / `ChangeMeNow!2025`) and 100 example phone numbers across multiple area codes.

## Docker workflow

```bash
make build
make up
```

The compose file builds service images, starts PostgreSQL, and runs Nginx as the reverse proxy. Static assets from the admin service are served through Nginx at `/static/` on `admin.example.com`.

## Deployment checklist

1. Provision DNS records for `api.example.com`, `admin.example.com`, and `www.example.com` pointing to your load balancer.
2. Prepare environment files with production secrets and Postgres credentials.
3. Build and push container images (or run `docker compose build` on the host).
4. Obtain TLS certificates:
   ```bash
   docker run --rm -it \
     -v certs:/etc/letsencrypt \
     -v $(pwd)/infra/deploy/certbot-renew.sh:/certbot-renew.sh \
     certbot/certbot \
     /certbot-renew.sh api.example.com admin@example.com
   ```
   Repeat for each subdomain.
5. Deploy docker compose in detached mode: `docker compose up -d`.
6. Set up a cron job to renew certificates monthly using the helper script (e.g., `/usr/local/bin/certbot-renew.sh api.example.com admin@example.com`).
7. Monitor `/v1/healthz`, `/v1/ready`, and `/v1/metrics` endpoints for operational visibility.

## API usage examples

All commands assume services are running locally. Replace hosts with production domains when applicable.

```bash
# 1. List top area-code prefixes with counts
curl 'http://localhost:8000/v1/prefixes?limit=5'

# 2. Filter prefixes starting with 21*
curl 'http://localhost:8000/v1/prefixes?q=21'

# 3. Search for related numbers
curl 'http://localhost:8000/v1/search?area_code=415&number=5551234'

# 4. Public health check
curl 'http://localhost:8000/v1/healthz'

# 5. Admin login (JSON API)
curl -X POST -c cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"ChangeMeNow!2025"}' \
  http://localhost:8001/v1/auth/login

# 6. Fetch authenticated admin profile
curl -b cookies.txt http://localhost:8001/v1/auth/me

# 7. Create a phone number via admin API
curl -X POST -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"area_code":"646","phone_number":"5559876","cost":175}' \
  http://localhost:8001/v1/numbers

# 8. Bulk upload numbers (dry-run)
curl -X POST -b cookies.txt -F dry_run=true -F upsert=true \
  -F file=@numbers.csv http://localhost:8001/v1/numbers/bulk-upload

# 9. Change admin credentials
curl -X POST -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"current_password":"ChangeMeNow!2025","new_username":"root","new_password":"UltraSecure!2025"}' \
  http://localhost:8001/v1/auth/change-credentials

# 10. Admin readiness probe
curl http://localhost:8001/v1/ready
```

## Observability

- `/v1/healthz`: service liveness and metadata.
- `/v1/ready`: database readiness check (returns 503 on failure).
- `/v1/metrics`: Prometheus text exposition with total number count (API service only).

## Troubleshooting

- **Migrations fail**: Ensure both services point to the same database and that credentials match. Run `python services/api/manage.py migrate` directly for detailed output.
- **Admin login lockout**: The login endpoint enforces `LOGIN_RATE_LIMIT`. Wait for the window to expire or adjust `RATE_LIMITS_LOGIN` in your environment.
- **CORS errors**: Confirm `CORS_ALLOWLIST` matches the exact frontend origin (including scheme).
- **Switch to SQLite**: Set `DATABASE_ENGINE=sqlite` (default) and remove Postgres env vars. SQLite files live under `data/` when using Docker.

## License

This repository is provided as reference implementation and may require additional hardening before production use.
