import docker
import time
import psycopg2
import uuid

# Connect to Docker running on this machine
client = docker.from_env()

POSTGRES_IMAGE = "postgres:16"
TIMESCALE_IMAGE = "timescale/timescaledb:latest-pg16"

def create_session_containers():
    """
    Spins up one vanilla Postgres container and one TimescaleDB container.
    Returns connection details for both.
    Each container gets a unique name so multiple sessions don't clash.
    """

    # Unique ID for this benchmark session
    session_id = str(uuid.uuid4())[:8]

    pg_name = f"pg-{session_id}"
    ts_name = f"ts-{session_id}"

    # Common environment variables for both containers
    env = {
        "POSTGRES_PASSWORD": "benchmark",
        "POSTGRES_DB": "benchdb",
        "POSTGRES_USER": "bench"
    }

    # Start vanilla Postgres container
    pg_container = client.containers.run(
        POSTGRES_IMAGE,
        name=pg_name,
        environment=env,
        ports={"5432/tcp": None},  # None = let Docker pick a free port automatically
        detach=True,               # Run in background
        remove=False               # Don't auto-remove — we'll do it manually
    )

    # Start TimescaleDB container
    ts_container = client.containers.run(
        TIMESCALE_IMAGE,
        name=ts_name,
        environment=env,
        ports={"5432/tcp": None},
        detach=True,
        remove=False
    )

    # Wait for both to be ready
    pg_port = wait_for_postgres(pg_container, "bench", "benchmark", "benchdb")
    ts_port = wait_for_postgres(ts_container, "bench", "benchmark", "benchdb")

    return {
        "session_id": session_id,
        "postgres": {
            "container_id": pg_container.id,
            "port": pg_port,
            "host": "localhost",
            "user": "bench",
            "password": "benchmark",
            "dbname": "benchdb"
        },
        "timescale": {
            "container_id": ts_container.id,
            "port": ts_port,
            "host": "localhost",
            "user": "bench",
            "password": "benchmark",
            "dbname": "benchdb"
        }
    }


def wait_for_postgres(container, user, password, dbname, timeout=60):
    """
    Polls the container every second until Postgres is ready to accept connections.
    Returns the host port once ready.
    Raises an error if it takes longer than timeout seconds.
    """
    start = time.time()

    while time.time() - start < timeout:
        # Reload container info to get the assigned port
        container.reload()
        ports = container.ports.get("5432/tcp")

        if ports:
            host_port = int(ports[0]["HostPort"])

            try:
                # Try to actually connect
                conn = psycopg2.connect(
                    host="localhost",
                    port=host_port,
                    user=user,
                    password=password,
                    dbname=dbname,
                    connect_timeout=2
                )
                conn.close()
                return host_port  # Connection succeeded — container is ready

            except psycopg2.OperationalError:
                pass  # Not ready yet — keep waiting

        time.sleep(1)

    raise TimeoutError(f"Container {container.name} did not become ready in {timeout}s")


def destroy_session_containers(session_info):
    """
    Stops and removes both containers for a session.
    Always called after benchmark is done — or if anything goes wrong.
    """
    for key in ["postgres", "timescale"]:
        container_id = session_info[key]["container_id"]
        try:
            container = client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove()
            print(f"Destroyed container {container_id[:12]}")
        except Exception as e:
            print(f"Warning: could not destroy container {container_id[:12]}: {e}")
