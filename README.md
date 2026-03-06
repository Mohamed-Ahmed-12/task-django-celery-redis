# Task Django Celery Redis

A backend assessment project implementing a **B2B SaaS transaction pipeline** using **Django, DRF, PostgreSQL, Redis, and Celery**.  
Clients submit batches of transactions via a REST API, and each transaction is validated asynchronously through a mock third-party service.

---

## ⚙️ Setup & Run Instructions

### 1. Prerequisites
- Docker  
- Docker Compose  

### 2. Run the stack
```bash
git clone https://github.com/Mohamed-Ahmed-12/task-django-celery-redis.git
cd task-django-celery-redis
docker-compose up --build
```

This will start:
- Django app (with migrations auto-applied)
- PostgreSQL database  
- Redis instance  
- Celery worker  

### 3. Default Credentials
- **Username:** `admin`  
- **Password:** `admin123`  
- **Token:** Obtain via `/api/token/` endpoint 

---

## 📡 API Endpoints

| Method | Endpoint                  | Auth Required| Description |
|--------|---------------------------|--------------|-------------|
| POST   | `/api/auth/login/`        |No |Login with credientials |
| POST   | `/api/mock-validate/`        |No |Mock validation service |
| POST   | `/api/batches/`           |Yes |Submit a new batch of transactions |
| GET    | `/api/batches/{id}/`      |Yes |Retrieve batch status & transactions |
| GET    | `/api/batches/`           |Yes |List all batches for authenticated client (paginated) |
| GET   | `/api/transactions/{id}/` |Yes |Retrieve status of a single transaction |

---


## 🔍 Example Usage

### 1. Authentication Endpoint
Request:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
 "username":"admin",
 "password":"admin123"
}'

```

Response (200 OK):

```json
{
    "status": "success",
    "code": 200,
    "data": {
        "token": "f7130298e447689c4ccca1953f0457a195ab7f58"
    },
    "message": "Operation completed",
    "errors": null
}
```
Response (400 Bad Request):

```json
{
    "status":"error",
    "code":400,
    "data":null,
    "message":"An error occurred",
    "errors":{
        "username":["This field is required."],
        "password":["This field is required."]
    }
}
```
###  Authentication Usage:
Once authenticated, include the token in the Authorization header for all protected endpoints:
```
Authorization: Token <token>
```
---
### 2. Mock validation service Endpoint
Request:
```bash
curl -X POST http://localhost:8000/api/mock-validate/ \
-H "Content-Type: application/json" \
-d '{
  "payload": {
    "any": "data",
    "you": "want"
  }
}'

```
Response (200 OK):

```json
{
    "status": "success",
    "code": 200,
    "data": {        
        "valid": true,
        "provider_ref": "EXT-7421",
        "latency": 3.42
    },
    "message": "Operation completed",
    "errors": null
}
```
Response (400 Bad Request):

```json
{
    "status":"error",
    "code":400,
    "data":null,
    "message":"An error occurred",
    "errors":{
        "error": "External API Timeout/Unavailable"
    }
}
```

### Mock Service Characteristics
| Feature | Value     | 
| :-------- | :------- |
| `Latency Range` | `3-5 seconds (randomized)` |
| `Failure Rate` | `20% (simulated 503 errors)` |
| `Authentication` | `None required (public endpoint)` |
| `Provider Reference` | `Generated as EXT-XXXX (1000-9999)` |
---
### 3. Batch Endpoints

#### Submit a new batch of transactions
Request:
```bash
curl -X POST http://localhost:8000/api/batches/ \
-H "Content-Type: application/json" \
-H "Authorization: Token <token>" \
-d '{
    "transactions": [
        {
            "payload": {
                "id": 1,
                "amount": 423.82,
                "currency": "USD",
                "merchant": "TechStore",
                "type": "purchase"
            }
        }
    ]    
'

```
Response (200 OK):

```json
{
    "status": "success",
    "code": 202,
    "data": {
        "batch_id": "1ee45c01-543e-487e-b305-43e08850dae4"
    },
    "message": "Operation completed",
    "errors": null
}
```
Response (400 Bad Request):

```json

{
    "status": "error",
    "code": 400,
    "data": null,
    "message": "An error occurred",
    "errors": {
        "detail": "list of Transactions must be exist"
    }
}

```
#### Retrieve batch status & transactions 
Request:
```bash
curl -X GET http://localhost:8000/api/batches/be2875cd-a42c-443e-8190-71bcf73bd81e \
-H "Content-Type: application/json" \
-H "Authorization: Token <token>" \

```
Response (200 OK):

```json
{
    "status": "success",
    "code": 200,
    "data": {
        "id": "be2875cd-a42c-443e-8190-71bcf73bd81e",
        "client": 1,
        "status": "COMPLETED",
        "created_at": "2026-03-05T15:47:07.071241Z",
        "updated_at": "2026-03-05T15:47:07.071253Z",
        "transactions": [
            {
                "id": 3247,
                "status": "COMPLETED",
                "created_at": "2026-03-05T15:47:07.130162Z",
                "updated_at": "2026-03-05T15:47:07.130167Z",
                "payload": {
                    "id": 100,
                    "type": "finance",
                    "amount": 500.0,
                    "currency": "USD",
                    "merchant": "SavingsDeposit"
                },
                "result": {
                    "code": 200,
                    "data": {
                        "valid": true,
                        "latency": 3.32386150471972,
                        "provider_ref": "EXT-3516"
                    },
                    "errors": null,
                    "status": "success",
                    "message": "Operation completed"
                }
            }
        
        ]
    },
    "message": "Operation completed",
    "errors": null
}
```

#### List all batches for authenticated client (paginated)
Request:
```bash
curl -X GET http://localhost:8000/api/batches/?page=2 \
-H "Content-Type: application/json" \
-H "Authorization: Token <token>" \

```
Response (200 OK):

```json
{
    "status": "success",
    "code": 200,
    "data": {
        "count": 3,
        "next": null,
        "previous": "http://127.0.0.1:8000/api/batches/",
        "results": [
            {
                "id": "be2875cd-a42c-443e-8190-71bcf73bd81e",
                "client": 1,
                "status": "COMPLETED",
                "created_at": "2026-03-05T15:47:07.071241Z",
                "updated_at": "2026-03-05T15:47:07.071253Z",
                "transactions": [
                    {
                        "id": 3247,
                        "status": "COMPLETED",
                        "created_at": "2026-03-05T15:47:07.130162Z",
                        "updated_at": "2026-03-05T15:47:07.130167Z",
                        "payload": {
                            "id": 100,
                            "type": "finance",
                            "amount": 500.0,
                            "currency": "USD",
                            "merchant": "SavingsDeposit"
                        },
                        "result": {
                            "code": 200,
                            "data": {
                                "valid": true,
                                "latency": 3.32386150471972,
                                "provider_ref": "EXT-3516"
                            },
                            "errors": null,
                            "status": "success",
                            "message": "Operation completed"
                        }
                    },
                ]
            }
        ]
    }
}
```
### 4. Transaction Endpoint

#### Retrieve status of a single transaction
Request:
```bash
curl -X GET http://localhost:8000/api/transactions/3237 \
-H "Content-Type: application/json" \
-H "Authorization: Token <token>" \

```

Response (200 Ok):
```json
{
    "status": "success",
    "code": 200,
    "data": {
        "status": "COMPLETED"
    },
    "message": "Operation completed",
    "errors": null
}
```



## 📊 Database Schema

The data layer is optimized for asynchronous workflows, using **UUIDs** for batch tracking and **JSONB** fields for flexible transaction payloads.

### 🔐 Authentication Layer
| Model | Relationship | Description |
| :--- | :--- | :--- |
| **User** | `django.contrib.auth` | Primary identity for B2B clients. |
| **Token** | `OneToOne` with **User** | Standard DRF Token-based authentication. |

### 💳 Transaction Pipeline Layer

#### **Batch Model**
*Represents a collection of transactions submitted in a single request.*

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | **UUID** | Primary Key (Secure, non-sequential tracking). |
| `client` | **ForeignKey** | Links to the `User` who submitted the batch. |
| `status` | **ChoiceField** | `PENDING` ➔ `PROCESSING` ➔ `COMPLETED` \| `FAILED` |
| `created_at` | **DateTime** | Timestamp of submission. |
| `updated_at` | **DateTime** | Last status transition timestamp. |

#### **Transaction Model**
*The atomic unit of work processed by the Celery worker.*

| Field | Type | Description |
| :--- | :--- | :--- |
| `batch` | **ForeignKey** | Parent Batch (Related Name: `transactions`). |
| `payload` | **JSONField** | Raw transaction data (amount, merchant, etc.). |
| `result` | **JSONField** | Detailed response/errors from the validation service. |
| `status` | **ChoiceField** | Individual lifecycle: `PENDING` to `COMPLETED`. |
| `created_at` | **DateTime** | Record creation time. |
| `updated_at` | **DateTime** | Worker completion time. |

---
## Project Structure
```bash
src/
├── accounts/              
│   ├── models.py          # User model (extends Django User)
│   ├── urls.py            # /api/auth/login/ endpoint
│   └── views.py           # CustomAuthToken for token-based auth
├── main/                  # Core business logic app
│   ├── models.py          # Batch, Transaction models with status enums
│   ├── serializers.py     # DRF serializers for API validation
│   ├── tasks.py           # Celery task definitions
│   ├── views.py           # Batch/Transaction API views
│   └── urls.py            # /api/batches/, /api/transactions/ routes
├── project/               # Django project configuration
│   ├── settings.py        # Django + Celery configuration
│   ├── celery.py          # Celery app initialization
│   ├── services/          # External service mocks
│   │   └── external_validator.py
│   ├── utils/             # Custom utilities
│   │   └── render.py      # CustomJSONRenderer
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI application entry point
│   └── asgi.py            # ASGI application entry point
└── manage.py              # Django management script
```

## 🛠️ Tech Stack
- **Backend:** Django, Django REST Framework  
- **Database:** PostgreSQL  
- **Queue & Worker:** Redis + Celery  
- **Containerization:** Docker & Docker Compose  

---



## Scaling to 1M Requests/Minute
To scale this system from 1,000 requests/day to 1,000,000 requests/minute, several architectural strategies are required:

- Horizontal Scaling of API Layer :
    Deploy multiple Django application instances behind a load balancer (e.g., Nginx, HAProxy, or AWS ALB). This ensures requests are evenly distributed and no single node becomes a bottleneck.

- Queue Partitioning & Worker Pools :
    Partition Celery queues by client, batch size, or transaction type. Scale Celery workers horizontally across multiple nodes, allowing parallel processing of millions of transactions.

- Database Optimization:
    Use read replicas to offload query traffic.
    Implement table partitioning or sharding for the Transaction table to handle massive write volumes.
    Add indexes on frequently queried fields (status, created_at).
    Employ connection pooling for efficient DB access.

- Caching & Rate Limiting  
    Redis can be used for caching hot data (e.g., batch summaries) and enforcing rate limits to protect the system from abusive traffic.

- Event Streaming  
    Introduce Kafka or AWS Kinesis for ingestion pipelines at extreme scale. This decouples ingestion from processing and ensures durability under spikes.

- Monitoring & Observability  
    Use Prometheus + Grafana (or AWS CloudWatch) to monitor throughput, latency, and worker health. Implement distributed tracing for bottleneck analysis.

## AWS Production Architecture
For production deployment on AWS, replace self‑managed components with managed services:

- API Layer

    1. Deploy Django app on Amazon ECS (Fargate) or EKS (Kubernetes) for container orchestration.
    2. Use AWS Application Load Balancer (ALB) for traffic distribution.

- Database
    1. Replace PostgreSQL with Amazon RDS (PostgreSQL) for automated backups, scaling, and failover.
    2. Enable read replicas for query scaling.

- Queue & Workers
    1. Replace Redis with Amazon SQS for message queuing.
    2. Celery workers consume from SQS, deployed on ECS/EKS.
    3. For serverless workloads, consider AWS Lambda workers triggered by SQS events.

- Caching
    1. Use Amazon ElastiCache (Redis) for caching and rate limiting.

- Storage & Logging
    1. Store logs, artifacts, and batch payloads in Amazon S3.
    2. Use AWS CloudWatch Logs for centralized logging.

- Monitoring & Security
    1. AWS CloudWatch for metrics and alarms.
    2. AWS X‑Ray for distributed tracing.
    3. AWS IAM for fine‑grained access control.