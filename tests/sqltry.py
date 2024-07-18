import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='eba',
        password='ebikesafrica',
        database='EBA_backend_db'
    )
    if conn.is_connected():
        print("Successfully connected to MySQL")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if conn.is_connected():
        conn.close()
