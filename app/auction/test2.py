from django.core.cache import cache
from django.conf import settings
import redis

settings.configure()

redis_client = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])


asta_id = "1"
user_id = "matteofoschi"
amount = 100

redis_key = f"asta:{asta_id}"
redis_client.zadd(redis_key, {user_id: amount})

data = redis_client.get(redis_key)
print(data)
print("Information from REDIS CHACHE")
