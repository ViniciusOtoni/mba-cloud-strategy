import os
import pyodbc
from flask import Flask, jsonify

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "serverdindin.database.windows.net"),
    "database": os.getenv("DB_NAME", "dbdindin"),
    "username": os.getenv("DB_USER", "vini123"),
    "password": os.getenv("DB_PASSWORD", "viniadm123!"),
    "driver": "{ODBC Driver 18 for SQL Server}",
}

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)


@app.route("/")
def index():
    return jsonify({
        "app": "dindinapp",
        "status": "running",
        "message": "API conectada ao Azure SQL Database"
    })


@app.route("/health")
def health():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/db/tables")
def list_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"tables": tables}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
