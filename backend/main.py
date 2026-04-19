from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, benchmark

app = FastAPI(
    title="Postgres to Tiger API",
    description="Benchmark vanilla Postgres vs TimescaleDB in ephemeral containers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(benchmark.router)
