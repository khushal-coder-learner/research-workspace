from app.infrastructure.redis.client import redis_client

redis_client.set("ping", "pong")

print(redis_client.get("ping"))