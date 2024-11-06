from flask import Flask, jsonify, render_template, request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, Table,Column, Integer, ForeignKey
import pymysql
import secrets

app = Flask(__name__) 

app.config['SECRET_KEY'] = 'Super_Secret_Key_Temp'

# DB connection 
# note that '@' MUST be replaced with its URL-encode special character 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://library:Libr%40ry1930!!@127.0.0.1:3306/personal_library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

GenreBooks = Table(
    'bookgenres', db.Model.metadata,
    Column('BookID', Integer, ForeignKey('books.BookID', ondelete='CASCADE'), primary_key=True),
    Column('GenreID', Integer, ForeignKey('genres.GenreID', ondelete='CASCADE'), primary_key=True)
)

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

    genres = db.relationship('Genre', secondary='bookgenres', backref=db.backref('books', lazy='dynamic'))
   

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

        # Add the book to the session first, then append genres
        db.session.add(new_book) 
        

        # Add the selected genres to the book
        for genre_id in selected_genres:
            genre = Genre.query.get(int(genre_id)) # Fetch the genre by ID
            if genre: # check if genre exists
                new_book.genres.append(genre) # Add the genre to the book's genres

        # Commit the session to save the book and its related genres
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))

    # Fetch all genres for the form
    genres = Genre.query.all()
    return render_template('add_book.html', genres=genres)


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    print(f"Editing book with ID: {book_id}") #debug
    book = Book.query.get_or_404(book_id)
    genres = Genre.query.all()

    # Prepare assigned genre IDs to pass to the template edit_book so the checkboxes can be pre-selected
    assigned_genre_ids = [genre.GenreID for genre in book.genres]
        
    if request.method == 'POST':
        print(f"Form data: {request.form}")  # Log the form data
        book.Title = request.form['title']
        book.Author = request.form['author']
        book.Status = request.form['status']
        book.Format = request.form['format']
       
       
        # Get the selected genres from the form
        selected_genres = request.form.getlist('genres') # This is a list of GenreID values from checkboxes

        # Ensure genres are in integer format
        selected_genres = [int(genre_id) for genre_id in selected_genres]

        # Current genre IDs associated with the book
        current_genre_ids = [genre.GenreID for genre in book.genres]


        # 1. Remove unselected genres
        for genre in book.genres:
            if genre.GenreID not in selected_genres:
                book.genres.remove(genre)  # Remove the genre from the book (in 'bookgenres' table)

        # 2. Add new genres (that are selected but not yet associated)
        for genre_id in selected_genres:
            if genre_id not in current_genre_ids:
                genre = Genre.query.get(genre_id)
                if genre: # If the genre exists
                    book.genres.append(genre)  # Add the genre to the book (in 'bookgenres' table)

        try:
            # Commit the changes to the database 
            db.session.commit()
            flash('Book updated successfully!')
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")  # This will print the error in the console
            flash(f"Error: {e}", 'error')
            return redirect(url_for('search_book'))

    return render_template('edit_book.html', book=book, genres=genres, assigned_genre_ids=assigned_genre_ids)

@app.route('/search_book',methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        search_query = request.form['search_query']
        # SQLAchemey to filter books by name (case insensitive)
        # f"%{search_query}%" -> % sql wildcard matches 0 or more characters
        # Any book Title contraining the sub-string put in f"%{search_query}% will be searched for
        books = Book.query.filter(Book.Title.ilike(f"%{search_query}%")).all() 

        # No book found 
        if not books:
            flash('No books found matching your search. :(')

            return render_template('search_results.html', books=books, query=search_query)

    return render_template('search_book.html')

@app.route('/search_results', methods=['GET'])
def search_results():
    search_query = request.args.get('search_query')  # For GET, use `args`
    books = Book.query.filter(Book.Title.ilike(f"%{search_query}%")).all()
    return render_template('search_results.html', books=books, search_query=search_query)



if __name__ == "__main__":
    app.run(debug=True)
