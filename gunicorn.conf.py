import multiprocessing

bind = "0.0.0.0:8000"
# Reduce workers to lower memory footprint on small instances
workers = 1
# Use threads to handle some concurrency without forking many processes
worker_class = "gthread"
threads = 4
worker_connections = 100
# Increase request timeout to tolerate slow external calls (TON/Fragment)
timeout = 120
# Allow more time for graceful shutdown of workers
graceful_timeout = 120
# Keep connection alive a bit longer
keepalive = 5

# Recycle workers to mitigate memory leaks
max_requests = 100
max_requests_jitter = 20

# Статические файлы
static_root = "/app/static"
static_url = "/static/"