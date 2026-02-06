import random
import time
from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"]
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP error responses",
    ["endpoint"]
)

@app.route("/")
def home():
    with REQUEST_LATENCY.labels(endpoint="/").time():
        REQUEST_COUNT.labels("GET", "/", "200").inc()
        return "OK\n"

@app.route("/slow")
def slow():
    delay = random.uniform(0.5, 2.5)  # simulate latency
    time.sleep(delay)
    with REQUEST_LATENCY.labels(endpoint="/slow").time():
        REQUEST_COUNT.labels("GET", "/slow", "200").inc()
        return f"Slow response: {delay:.2f}s\n"

@app.route("/error")
def error():
    if random.random() < 0.4:  # 40% failure rate
        ERROR_COUNT.labels(endpoint="/error").inc()
        REQUEST_COUNT.labels("GET", "/error", "500").inc()
        return "Internal Server Error\n", 500
    REQUEST_COUNT.labels("GET", "/error", "200").inc()
    return "Recovered\n"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
