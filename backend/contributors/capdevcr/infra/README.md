# Serverless Lambdas on LocalStack with Terraform

---

## Contents

* [Architecture](#architecture)
* [Repository Layout](#repository-layout)
* [Prerequisites](#prerequisites)
* [Environment Variables](#environment-variables)
* [Start Local Services](#start-local-services)
* [Build Lambda Artifacts (ZIPs)](#build-lambda-artifacts-zips)
* [Deploy with Terraform](#deploy-with-terraform)
* [Test the Endpoints](#test-the-endpoints)
* [Iterate (Code/Deps Changes)](#iterate-codedeps-changes)
* [Tear Down](#tear-down)
* [Troubleshooting](#troubleshooting)

---

## Architecture

* **Lambda functions** (Python) with handlers:

  * `app.functions.login.src.app.handler` → `POST /login`
  * `app.functions.list_shipments.src.app.handler` → `POST /shipment/list`
* **API Gateway (HTTP)** → proxies requests to the corresponding Lambda.
* **LocalStack** → emulates AWS services locally (Lambda, API Gateway, IAM, Logs).
* **Postgres** → your DB container (reachable by Lambdas via Docker network).

---

## Repository Layout

```
contributors/
└─ name/
   ├─ shipments_lambdas/
   │  ├─ app/                          # import root "app"
   │  │  └─ functions/
   │  │     ├─ login/          /src/app.py   # def handler(event, context)
   │  │     └─ list_shipments/ /src/app.py   # def handler(event, context)
   │  └─ deploy/
   │     └─ build_functions_docker.ps1       # build script (Windows/PowerShell)
   └─ infra/
      ├─ build/                              # (generated) lambda ZIPs
      └─ terraform/
         versions.tf
         providers.tf
         variables.tf
         iam.tf
         lambda_functions.tf
         apigw.tf
         outputs.tf
```

> The Lambda ZIPs must include an **`app/`** folder at the root so imports like `from app.auth import ...` work.

---

## Prerequisites

* **Docker** & **Docker Compose v2** (`docker compose`)
* **Terraform** ≥ 1.6
* **PowerShell** (Windows) to run the build script (uses Docker internally)
* A `docker-compose.yml` at repo root with:

  * a **Postgres** service (e.g., `flask_db`)
  * a **LocalStack** service on the **same Docker network** (e.g., `local-dev`) with:

    * `LAMBDA_DOCKER_NETWORK=local-dev`
    * Docker socket mounted (`/var/run/docker.sock`)

---

## Environment Variables

These are passed to Lambdas via Terraform (`variables.tf`) and must match your DB service:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=shipments
POSTGRES_HOST=flask_db       # must be the Docker service name of your DB
POSTGRES_PORT=5432
SECRET_KEY=dev-secret
TOKEN_TTL_SECONDS=900
```

---

## Start Local Services

From the repository root:

```bash
docker compose up -d localstack flask_db
```

* Ensure **both** services are attached to the same network (e.g., `local-dev`).
* LocalStack must have `LAMBDA_DOCKER_NETWORK=local-dev` so Lambdas can resolve `flask_db`.

---

## Build Lambda Artifacts (ZIPs)

Use the provided build script (creates Linux-compatible wheels—important for `psycopg`—and bundles `app/` + site-packages):

```powershell
pwsh ./contributors/*name*/shipments_lambdas/deploy/build_functions_docker.ps1
```

Output:

```
contributors/*name*/infra/build/login.zip
contributors/*name*/infra/build/list_shipments.zip
```

---

## Deploy with Terraform

```bash
cd contributors/*name*/infra/terraform
terraform init
terraform apply -auto-approve
```

On success:

```bash
terraform output -raw http_api_url
# Example (LocalStack):
# https://abc123.execute-api.localhost.localstack.cloud:4566
```

---

## Test the Endpoints

1. **Login** (returns a JWT):

```bash
API=$(terraform output -raw http_api_url)

curl -s -X POST "$API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"store_manager"}'
```

Expected:

```json
{"access_token":"<jwt>","token_type":"Bearer"}
```

2. **List shipments** (authorized):

```bash
TOKEN="<paste_access_token_here>"

curl -s -X POST "$API/shipment/list" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

> Ensure your DB schema/data exist (run migrations/seeds against `flask_db` as you normally do).

---

## Iterate (Code/Deps Changes)

Whenever you change Python code or dependencies:

```bash
# Rebuild ZIPs
pwsh ./contributors/capdevcr/shipments_lambdas/deploy/build_functions_docker.ps1

# Re-deploy
cd contributors/capdevcr/infra/terraform
terraform apply -auto-approve
```

---

## Tear Down

```bash
cd contributors/capdevcr/infra/terraform
terraform destroy -auto-approve

docker compose down
```

---

## Troubleshooting

**`Unable to import module 'app.functions.*'`**

* Verify the ZIP contains an **`app/`** directory at the root.
* Confirm Terraform handlers:

  * `app.functions.login.src.app.handler`
  * `app.functions.list_shipments.src.app.handler`

**Lambda cannot connect to DB**

* `POSTGRES_HOST` must equal your DB **service name** (default: `flask_db`).
* LocalStack must be started with `LAMBDA_DOCKER_NETWORK=local-dev` and DB on that network.
* Check logs: `docker logs localstack -f`.

**`psycopg`/binary errors**

* Always build inside the Linux container (the script already does this).
* Don’t `pip install` on Windows into the ZIP.

**API URL looks wrong or empty**

* Re-run: `terraform output -raw http_api_url`
* Confirm LocalStack is healthy: `docker logs localstack`

---
