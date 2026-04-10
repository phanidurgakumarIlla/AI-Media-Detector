import pymysql

# Connect directly to the MySQL server without specifying a database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1325',
    port=3306
)

try:
    with connection.cursor() as cursor:
        # Create the AI Detector database if it doesn't already exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS ai_detector_db")
        print("Successfully ensured database 'ai_detector_db' exists.")
finally:
    connection.close()
