from flask import Flask, request
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST, Gauge
import time
import psutil
import threading

app = Flask(__name__)

REQUEST_COUNTER = Counter("app_requests_total", "Total requests by endpoint", ["method", "endpoint"])
REQUEST_LATENCY = Summary("app_request_latency_seconds", "Request latency by endpoint", ["endpoint"])
CPU_USAGE = Gauge("app_cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("app_memory_usage_bytes", "Memory usage in bytes")

@app.route("/")
@REQUEST_LATENCY.labels("/").time()
def index():
    REQUEST_COUNTER.labels(request.method, request.path).inc()
    return "Hello from a fully monitored Flask app!"

@app.route("/about")
@REQUEST_LATENCY.labels("/about").time()
def about():
    REQUEST_COUNTER.labels(request.method, request.path).inc()
    return "This is the about page."

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

def update_system_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent(interval=1))
        MEMORY_USAGE.set(psutil.virtual_memory().used)

if __name__ == "__main__":
    # Iniciar el hilo para métricas de sistema
    threading.Thread(target=update_system_metrics, daemon=True).start()
    
    app.run(host="0.0.0.0", port=8000)