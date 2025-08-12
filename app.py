import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Database connection details from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'my-secret-pw')
DB_NAME = os.environ.get('DB_NAME', 'mysql') # Default database

def get_db_connection():
    """Creates a connection to the database."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None

@app.route('/')
def index():
    return "<h1>Welcome to the Flask App!</h1><p>Go to /db_version to see the MariaDB version.</p>"

@app.route('/db_version')
def get_db_version():
    """Connects to the database and returns the version."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT VERSION() as version')
            result = cursor.fetchone()
            return jsonify(result)
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
