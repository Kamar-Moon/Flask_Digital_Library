from flask import Flask, jsonify, render_template, request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql
import secrets

app = Flask(__name__) 

app.config['SECRET_KEY'] = 'Super_Secret_Key_Temp'

# DB connection 
# note that '@' MUST be replaced with its URL-encode special character 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://library:Libr%40ry1930!!@127.0.0.1:3306/personal_library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Genre(db.Model):
    __tablename__ = 'genres'
    GenreID = db.Column(db.Integer,primary_key=True)
    GenreName = db.Column(db.String(255),nullable=False)

class Book(db.Model):
    __tablename__ = 'books'
    BookID = db.Column(db.Integer,primary_key=True)
    Title =  db.Column(db.String(255),nullable=False)
    Author = db.Column(db.String(255),nullable=False)
    Status = db.Column(db.Enum('read','purchased','in progress','not purchased'),nullable=False)
    Format = db.Column(db.Enum('Hardcover', 'Paperback', 'Ebook', 'Audiobook'), nullable=False)

class GenreBooks(db.Model):
    __tablename__ = 'bookgenres'  
    BookGenreID = db.Column(db.Integer,primary_key=True)
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID'), nullable=False)
    GenreID = db.Column(db.Integer, db.ForeignKey('genres.GenreID'), nullable=False) 

# Relationships between tables
book = db.relationship('Book', backref=db.backref('genre_books'))    
genre = db.relationship('Genre', backref=db.backref('genre_books', passive_deletes=True))
#allows access to the GenreBooks entries associated with a particular book
genre_books = db.relationship('GenreBooks', backref='book', cascade='all, delete-orphan')

@app.route("/")
def home():
    return render_template('base.html')

# Functions
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
    column_names = ['BookID', 'Title', 'Author', 'Status', 'Format']  # Adjust as per your actual columns
    data = fetch_data(query, column_names)  # Call the fetch_data function
    
    if data is not None:
        return jsonify(data)  # Return the list of dictionaries as JSON
    else:
        return jsonify(message="Error fetching data", status="error")



@app.route('/add_book', methods=['GET','POST'])
def add_book():
    error_message = None # Initilize the error message

    if request.method == 'POST':
        title = request.form['title']  
        author = request.form['author']  
        status = request.form['status'] 
        format = request.form['format'] 
        selected_genres = request.form.getlist('genres')  # Get the selected Generes as a list

        

        # Create a new Book instance
        new_book = Book(Title=title, Author=author, Status=status, Format=format)
        db.session.add(new_book)
        db.session.flush()  # Flush to get the BookID for GenreBooks

        # Add genres to GenreBooks table
        for genre_id in selected_genres:
            genre_book_entry = GenreBooks(BookID=new_book.BookID, GenreID=genre_id)
            db.session.add(genre_book_entry)
        
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('home'))

    # Fetch all genres for the form
    genres = Genre.query.all()
    return render_template('add_book.html', genres=genres)


if __name__ == "__main__":
    app.run(debug=True)
