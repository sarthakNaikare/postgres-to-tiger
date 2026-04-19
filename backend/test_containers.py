from services.container_manager import create_session_containers, destroy_session_containers

print("Starting containers...")
session = create_session_containers()

print(f"\nSession ID: {session['session_id']}")
print(f"Postgres running on port: {session['postgres']['port']}")
print(f"TimescaleDB running on port: {session['timescale']['port']}")

print("\nDestroying containers...")
destroy_session_containers(session)
print("Done. Both containers destroyed.")
