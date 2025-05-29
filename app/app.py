from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
from psycopg2 import OperationalError
import os
import time
from prometheus_flask_exporter import PrometheusMetrics
from metrics import *

app = Flask(__name__)

# Prometheus setup
metrics = PrometheusMetrics(app, path='/metrics')
init_metrics()
metrics.info('app_info', 'Application info', version='1.0.0', environment='development')


DB_CONFIG = {
    'host': 'host.docker.internal',
    'port': 5432,
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '0000'
}


def get_db_connection(retries=10, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            DB_CONNECTIONS.inc()
            print("Connected to PostgreSQL")
            return conn
        except OperationalError as e:
            attempt += 1
            DB_ERRORS.labels(operation='connect').inc()
            print(f"Attempt {attempt}/{retries} - Error: {e}")
            if attempt == retries:
                raise Exception("Database connection failed after retries.")
            time.sleep(delay)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                task TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        print("Database initialized")
    except Exception as e:
        DB_ERRORS.labels(operation='init').inc()
        print(f"Error initializing DB: {e}")
        raise
    finally:
        cursor.close()
        DB_CONNECTIONS.dec()
        conn.close()

@app.route('/todos', methods=['POST'])
def add_todo():
    start_time = time.time()
    data = request.get_json()
    if not data or 'task' not in data:
        REQUEST_COUNT.labels(method='POST', endpoint='/todos', status='400').inc()
        REQUEST_LATENCY.labels(method='POST', endpoint='/todos', status='400').observe(time.time() - start_time)
        return jsonify({"error": "Task is required"}), 400

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        timestamp = datetime.now()
        cursor.execute("INSERT INTO todos (task, timestamp) VALUES (%s, %s) RETURNING id", (data["task"], timestamp))
        todo_id = cursor.fetchone()[0]
        conn.commit()
        todo = {
            "id": todo_id,
            "task": data["task"],
            "timestamp": timestamp.isoformat()
        }
        TODO_CREATED.inc()
        status = '201'
    except Exception as e:
        DB_ERRORS.labels(operation='insert').inc()
        status = '500'
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        DB_CONNECTIONS.dec()
        conn.close()

    REQUEST_COUNT.labels(method='POST', endpoint='/todos', status=status).inc()
    REQUEST_LATENCY.labels(method='POST', endpoint='/todos', status=status).observe(time.time() - start_time)
    return jsonify(todo), 201

@app.route('/todos', methods=['GET'])
def list_todos():
    start_time = time.time()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, timestamp FROM todos")
        todos = cursor.fetchall()
        result = [{"id": r[0], "task": r[1], "timestamp": r[2].isoformat()} for r in todos]
        TODO_LIST_REQUESTS.inc()
        status = '200'
    except Exception as e:
        DB_ERRORS.labels(operation='select').inc()
        status = '500'
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        DB_CONNECTIONS.dec()
        conn.close()

    REQUEST_COUNT.labels(method='GET', endpoint='/todos', status=status).inc()
    REQUEST_LATENCY.labels(method='GET', endpoint='/todos', status=status).observe(time.time() - start_time)
    return jsonify(result), 200

# Start application
print("Starting app...")
init_db()

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
