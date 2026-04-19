import docker
import time
import threading

# Any benchmark container older than this gets force-killed
MAX_CONTAINER_AGE_SECONDS = 180  # 3 minutes — well above our 90s benchmark

client = docker.from_env()


def kill_zombie_containers():
    """
    Finds and destroys any benchmark containers that have been
    running longer than MAX_CONTAINER_AGE_SECONDS.
    Our containers are named pg-{session_id} and ts-{session_id}
    so we can identify them easily.
    """
    try:
        all_containers = client.containers.list()

        for container in all_containers:
            name = container.name

            # Only touch our benchmark containers — leave everything else alone
            if not (name.startswith("pg-") or name.startswith("ts-")):
                continue

            # Calculate how long this container has been running
            # Docker gives us the start time as a string like "2024-01-01T12:00:00Z"
            started_at = container.attrs["State"]["StartedAt"]
            started_ts = parse_docker_time(started_at)
            age_seconds = time.time() - started_ts

            if age_seconds > MAX_CONTAINER_AGE_SECONDS:
                print(f"Killing zombie container {name} (age: {int(age_seconds)}s)")
                try:
                    container.stop(timeout=3)
                    container.remove()
                    print(f"Zombie {name} destroyed")
                except Exception as e:
                    print(f"Could not kill {name}: {e}")

    except Exception as e:
        print(f"Cleanup error: {e}")


def parse_docker_time(time_str: str) -> float:
    """
    Converts Docker's timestamp string to a Unix timestamp (float).
    Example input: "2024-01-15T10:30:00.123456789Z"
    """
    from datetime import datetime, timezone

    # Trim nanoseconds — Python only handles microseconds
    if "." in time_str:
        base, frac = time_str.split(".")
        frac = frac[:6]  # Keep only microseconds
        time_str = f"{base}.{frac}+00:00"
    else:
        time_str = time_str.replace("Z", "+00:00")

    dt = datetime.fromisoformat(time_str)
    return dt.timestamp()


def start_cleanup_watchdog(interval_seconds: int = 60):
    """
    Starts a background thread that runs kill_zombie_containers
    every interval_seconds. Starts automatically when FastAPI starts.
    """
    def watchdog_loop():
        print(f"Zombie watchdog started — checking every {interval_seconds}s")
        while True:
            kill_zombie_containers()
            time.sleep(interval_seconds)

    thread = threading.Thread(target=watchdog_loop, daemon=True)
    thread.start()
