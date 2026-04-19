import time
import threading


MAX_CONTAINER_AGE_SECONDS = 180


def kill_zombie_containers():
    """
    Only runs in real Docker mode — skipped in demo mode.
    """
    import os
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        return

    try:
        import docker
        client = docker.from_env()
        all_containers = client.containers.list()

        for container in all_containers:
            name = container.name
            if not (name.startswith("pg-") or name.startswith("ts-")):
                continue

            started_at = container.attrs["State"]["StartedAt"]
            started_ts = parse_docker_time(started_at)
            age_seconds = time.time() - started_ts

            if age_seconds > MAX_CONTAINER_AGE_SECONDS:
                print(f"Killing zombie container {name} (age: {int(age_seconds)}s)")
                try:
                    container.stop(timeout=3)
                    container.remove()
                except Exception as e:
                    print(f"Could not kill {name}: {e}")

    except Exception as e:
        print(f"Cleanup skipped: {e}")


def parse_docker_time(time_str: str) -> float:
    from datetime import datetime
    if "." in time_str:
        base, frac = time_str.split(".")
        frac = frac[:6]
        time_str = f"{base}.{frac}+00:00"
    else:
        time_str = time_str.replace("Z", "+00:00")
    return datetime.fromisoformat(time_str).timestamp()


def start_cleanup_watchdog(interval_seconds: int = 60):
    import os
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        print("Demo mode — watchdog disabled")
        return

    def watchdog_loop():
        print(f"Zombie watchdog started — checking every {interval_seconds}s")
        while True:
            kill_zombie_containers()
            time.sleep(interval_seconds)

    thread = threading.Thread(target=watchdog_loop, daemon=True)
    thread.start()
