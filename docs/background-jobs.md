# Background Jobs & Task Processing Guide

This document describes the asynchronous task processing architecture for **Career Copilot** using **Celery** and **Redis**.

---

## 1. Architecture Overview

When a student uploads a CV, long-running processes (PDF parsing via AI and Vector embedding computation) are executed asynchronously in background queues to guarantee API responses in `<500ms`.

### Task Pipeline

```
[POST /api/v1/cvs/upload]
         │
         ▼ (status: "uploaded")
 [parse_pdf_task] ── (queue: "pdf")
         │
         ▼ (status: "parsed")
 [generate_embeddings_task] ── (queue: "embeddings")
         │
         ▼ (status: "ready", embedding_status: "completed")
 [cv_chunks (pgvector 1536-dim)]
```

### Queue Definitions

| Queue Name   | Tasks                                                    | Description                                                                                      |
| ------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `pdf`        | `app.tasks.parse_pdf.parse_pdf_task`                     | Reads PDF from local storage (`file_path_relative`), parses structured sections, persists to DB. |
| `embeddings` | `app.tasks.generate_embeddings.generate_embeddings_task` | Splits sections, generates 1536-dim embeddings, stores in `cv_chunks`.                           |
| `matching`   | `app.tasks.bulk_match.bulk_match_task`                   | Bulk candidate-to-job matching operations.                                                       |
| `dlq`        | `app.tasks.dlq.handle_dlq_task`                          | Dead letter queue capturing permanent task failures after 3 failed retries.                      |

---

## 2. Running Services Locally

### Step 1: Start Redis & Postgres

Using Docker Compose:

```bash
docker-compose up -d redis postgres
```

### Step 2: Start Celery Worker

Navigate to the API directory and launch the worker:

```bash
cd apps/api
celery -A celery_worker.celery_app worker --queues=pdf,embeddings,matching,dlq --loglevel=info
```

### Step 3: Start Flower Monitoring Dashboard (Optional)

```bash
cd apps/api
celery -A celery_worker.celery_app flower --port=5555
```

Open **http://localhost:5555** in your browser to inspect workers, active queues, task progress, and failure rates in real-time.

---

## 3. Retries & Dead Letter Queue (DLQ) Strategy

- **Retry Limit:** Each task retries up to **3 times** with exponential backoff (`5s`, `10s`, `20s`).
- **Redis DLQ Handling:** Because Redis does not have native AMQP dead-letter exchanges, Celery tasks implement explicit failure escalation:
  1. If 3 retries fail, `MaxRetriesExceededError` is caught.
  2. The record status in `cvs` table is set to `"failed"`.
  3. A permanent error log is recorded in the `audit_logs` table (`action="CV_PARSE_FAILED"` or `"CV_EMBEDDING_FAILED"`).
  4. The poisoned payload is dispatched to `handle_dlq_task` on the `dlq` queue for operational inspection.

---

## 4. Checking Task Status via API

Clients can poll task execution state:

```http
GET /api/v1/tasks/{task_id}/status
```

**Response Example:**

```json
{
  "task_id": "c62b9a70-8bf1-4d32-8419-f9c18d9d5921",
  "status": "SUCCESS",
  "result": {
    "cv_id": "8fa886dc-f0cb-4654-945b-d3db0bc189f3",
    "status": "ready",
    "embedding_status": "completed",
    "chunks_created": 4
  },
  "error": null
}
```
