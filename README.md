# Bulk Certificate Generator

FastAPI backend for generating certificates in bulk.

## Live Demo

Swagger:
https://bulk-certificate-generator-vlk0.onrender.com/docs

API:
https://bulk-certificate-generator-vlk0.onrender.com

## Features

- Bulk certificate generation
- Recipient validation
- PDF certificate generation
- Background processing
- Status tracking
- Certificate download
- SQLite database
- FastAPI + Swagger

## Tech Stack

Python, FastAPI, SQLite, SQLAlchemy, Pydantic, ReportLab

## API

POST `/requests` - Create bulk certificate request

GET `/requests/{request_id}` - Check generation status

GET `/certificates/{certificate_id}/download` - Download certificate

GET `/health` - Health check

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload