import os
import time
import socket
from flask import Flask, jsonify
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "10"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

ZSET_KEY = os.getenv("REQUESTS_KEY", "requests:sliding_window")

@app.route("/")
def index():
    now = time.time()

    r.zadd(ZSET_KEY, {str(now): now})

    cutoff = now - WINDOW_SECONDS
    r.zremrangebyscore(ZSET_KEY, 0, cutoff)
    count = r.zcard(ZSET_KEY)

    response = {
        "hostname": socket.gethostname(),
        "window_seconds": WINDOW_SECONDS,
        "requests_in_window": count,
        "redis_key": ZSET_KEY
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
