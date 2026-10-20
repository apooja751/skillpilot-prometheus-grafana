
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = FastAPI(title="SkillPilot Monitoring API")

REQUEST_COUNT = Counter(
    "fastapi_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "fastapi_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)


@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        endpoint=request.url.path
    ).observe(duration)

    return response


@app.get("/")
def home():
    return {
        "message": "SkillPilot FastAPI Monitoring API is running",
        "status": "healthy"
    }


@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}


@app.get("/work")
def work():
    time.sleep(random.uniform(0.1, 0.5))
    return {"message": "Sample monitored workload completed"}


@app.get("/error")
def simulate_error():
    return Response(
        content='{"error":"Simulated server error"}',
        status_code=500,
        media_type="application/json"
    )


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
