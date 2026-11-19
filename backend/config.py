#DB_CONFIG = {
#  "host": "localhost",
#   "port": 3306,
#  "user": "root",
#   "password": "",
#   "database": "ai_project",
#   "charset": "utf8mb4",
#  }
# SERVER_PORT = 5000
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ai_project"),
    "charset": "utf8mb4",
}
SERVER_PORT = int(os.getenv("PORT", "5050"))
DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"