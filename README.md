# Bulk Certificate Generator

A FastAPI backend that accepts one bulk certificate-generation request,
validates recipients, generates PDF certificates using one predefined
template, tracks progress, and allows generated certificates to be downloaded.

## Requirements

- Python 3.10+
- pip

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Main endpoints

### Create bulk request

`POST /requests`

Example:

```json
{
  "event_name": "Python Workshop",
  "issuer_name": "ABC Organization",
  "recipients": [
    {
      "name": "Pranavu",
      "email": "pranavu@example.com"
    },
    {
      "name": "Arun",
      "email": "arun@example.com"
    }
  ]
}
```

The API immediately returns a `request_id` while generation continues
in a FastAPI background task.

### Check status

`GET /requests/{request_id}`

Example response:

```json
{
  "request_id": "...",
  "event_name": "Python Workshop",
  "issuer_name": "ABC Organization",
  "status": "completed",
  "total": 2,
  "generated": 2,
  "failed": 0,
  "certificates": [
    {
      "id": "...",
      "recipient_name": "Pranavu",
      "recipient_email": "pranavu@example.com",
      "status": "generated",
      "download_url": "/certificates/.../download",
      "error_message": null
    }
  ]
}
```

### Download certificate

`GET /certificates/{certificate_id}/download`

## Architecture

```text
Client
  |
  | POST /requests
  v
FastAPI
  |
  +--> Validate request
  |
  +--> SQLite
  |
  +--> BackgroundTasks
          |
          +--> Generate PDF for each recipient
          |
          +--> Update status
  |
  v
GET /requests/{id}
  |
  v
Progress/result

GET /certificates/{id}/download
  |
  v
PDF
```

## Why SQLite?

SQLite is a relational database and is enough for this assessment.
For production, PostgreSQL would be a better choice.

## Production improvements

For a production-scale system, replace FastAPI BackgroundTasks with
Celery/RQ + Redis, use PostgreSQL, object storage such as S3/Azure Blob,
authentication, rate limiting, retries, and proper job queues.
