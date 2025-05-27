# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'flask_request_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint', 'status']
)

# Database metrics
DB_CONNECTIONS = Gauge(
    'flask_db_connections_active',
    'Number of active database connections'
)

DB_ERRORS = Counter(
    'flask_db_errors_total',
    'Total number of database errors',
    ['operation']
)

# Todo-specific metrics
TODO_CREATED = Counter(
    'flask_todos_created_total',
    'Total number of todos created'
)

TODO_LIST_REQUESTS = Counter(
    'flask_todo_list_requests_total',
    'Total number of todo list requests'
)

def init_metrics():
    """Initialize Prometheus metrics."""
    print("Prometheus metrics initialized.")