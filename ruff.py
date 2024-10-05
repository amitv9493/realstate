import json

from django_redis import get_redis_connection


def main():
    conn = get_redis_connection("default")
    message = {
        "event_type": "CREATED",
        "model": "Showing",
        "content_id": 11,
        "description": None,
        "extra_data": {},
    }
    msg = json.dumps(message)
    conn.rpush("task-history-queue", msg)


if __name__ == "__main__":
    main()
