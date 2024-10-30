import sqlalchemy
from sqlalchemy import text
import pymysql

# Replace with your actual credentials
DATABASE_URI = 'mysql+pymysql://library:Libr%40ry1930!!@localhost:3306/personal_library'

# Create an engine
engine = sqlalchemy.create_engine(DATABASE_URI)

try:
    with engine.connect() as connection:
        # Use the text() function for the raw SQL query
        result = connection.execute(text("SELECT 1"))  # Correct way to execute a raw query
        print("Connection successful:", result.fetchone())
except Exception as e:
    print("Error connecting to the database:", str(e))
