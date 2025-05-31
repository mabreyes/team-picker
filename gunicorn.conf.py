"""Gunicorn configuration for Team Picker application.

Production-optimized settings for deployment on Render.com.
"""
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help limit memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "team-picker"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
