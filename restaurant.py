import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


cursor = conn.cursor()
print("============= RESTAURANT MENU ============")

cursor.execute("SELECT * FROM MENU")
for row in cursor.fetchall():
    print(f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")

print("==========================================")


cursor.close()
conn.close()