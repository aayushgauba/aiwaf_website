import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 100

# Timeout for requests
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "aiwaf_website"

# Worker tmp directory (for DigitalOcean)
worker_tmp_dir = "/dev/shm"
