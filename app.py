from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql

app = Flask(__name__)  

# DB connection 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://library:Libr%40ry1930!!@127.0.0.1:3306/personal_library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

@app.route("/")
def home():
    return "Hello User"

def fetch_data(query, column_names):
    #Fecth data from the db and return it as a list of dicionaries.
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()

            #convert each row tuple to a dictionary
            return [dict(zip(column_names, row)) for row in rows]
    except Exception as e:
        print(f"Error fecthing data: {str(e)}")
        return None

@app.route('/test', methods=['GET'])
def test_query():
    query = "SELECT * FROM books"  # Adjust your query as needed
    column_names = ['id', 'title', 'author', 'status', 'format']  # Adjust as per your actual columns
    data = fetch_data(query, column_names)  # Call the fetch_data function
    
    if data is not None:
        return jsonify(data)  # Return the list of dictionaries as JSON
    else:
        return jsonify(message="Error fetching data", status="error")

if __name__ == "__main__":
    app.run(debug=True)
