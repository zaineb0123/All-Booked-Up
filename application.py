import os
import csv
import datetime
import requests


from flask import Flask, session, jsonify, json, redirect, url_for, flash
from flask import render_template, request
from flask_session import Session
from psycopg2._psycopg import cursor
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config['DATABASE_URL'] = "postgres://nfsspsyiahwqcm:b48f99892e6cb2abe36ed571f673cef2997deb4f1d25da8fe571f283d62ec0f5@ec2-23-20-129-146.compute-1.amazonaws.com:5432/d7d6t9lfnshmas"
app.secret_key = b'_?:"{:L?L@#$ERDGFG:{:{'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))






@app.route('/', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        session.pop('login_id', None)        
        login_id = request.form.get("login_id")
        password = request.form.get("password")
        print(login_id)
        print(password)
        
        # Make sure user exists.
        if db.execute("SELECT * FROM users WHERE login_id = :login_id AND password = :password ", {"login_id": login_id, "password": password}).rowcount == 1:
            session['login_id'] = request.form.get("login_id")
            return redirect(url_for('homePage'))
        else:
            flash('Invalid user ID or password')
            return render_template("login.html")

    else:
        return render_template("login.html")
       



@app.route("/signup", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        login_id = request.form.get("login_id")
        password = request.form.get("password")
        db.execute("INSERT INTO users (first_name, last_name, login_id, password) VALUES(:first_name, :last_name, :login_id, :password)",
        {"first_name": first_name, "last_name" : last_name, "login_id": login_id, "password": password})
        db.commit()
        return render_template("login.html")

    else:
        return render_template("signUp.html")


@app.route("/homePage",  methods=['GET', 'POST'])
def homePage():
    if 'login_id' in session: 
        if request.method == 'POST':
            bookSearch = request.form.get("bookSearch")
            results = db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:bookSearch)) OR (LOWER(title) LIKE LOWER(:bookSearch)) OR (LOWER(author) LIKE LOWER(:bookSearch))  ", {"bookSearch" : '%' + bookSearch + '%'}).fetchall()
            if results is None:
                return render_template("error.html", message="No such book.")

            else:
                print("found book")
                return render_template("search.html", results=results, login_id=session['login_id'])
        else:        
            return render_template("homepage.html", login_id=session['login_id'])
    else:
        return 'You are not Logged in'


@app.route("/search")
def search():
     return render_template("search.html")



@app.route("/book_details",  methods=['GET', 'POST']) 
def book_details():
    if 'login_id' in session:
    #if request.method == 'GET':
        user_id = session['login_id']
        ISBN = request.args.get('isbn')
        book_details = db.execute("SELECT * FROM books WHERE isbn=:ISBN ", { "ISBN" : ISBN }).fetchone()
        book_review = db.execute("SELECT * FROM reviews WHERE isbn=:ISBN AND login_id=:user_id", { "ISBN" : ISBN, "user_id":user_id }).fetchone()
        

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "UONdS2vRM5tHX06Yy4Hikg", "isbns": ISBN})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']    
        result = {
        "title": book_details.title,
        "author": book_details.author,
        "year": book_details.year,
        "isbn": ISBN,
        "review_count": work_ratings_count,
        "average_score":average_rating 
        }





        if request.method == 'POST':
           
            if book_review == None:
                review_description = request.form.get("reviews")  
                ISBN = request.args.get('isbn') 
                rating = request.form.get("starsHidden")
                print("rating is", rating)
        
                db.execute("INSERT INTO reviews (rating, review_description, ISBN, login_id) VALUES(:rating, :review_description, :ISBN, :user_id)", {"rating":rating, "review_description":review_description, "ISBN":ISBN, "user_id":user_id})
                db.commit()
            else:
                flash('You cannot enter more than one review')
                    
        #return render_template("login.html")
        return render_template("book_details.html", book_details=book_details, book_review=book_review, login_id=session['login_id'], result=result)
    else:
        return 'You are not logged in'


@app.route("/api/<string:isbn>") 
def jsonfunction(isbn):
    #book_information = request.args.get('isbn')
    print("isbn is ", isbn)
    book_details = db.execute("SELECT * FROM books WHERE isbn=:isbn ", { "isbn" : isbn }).fetchone()
    
    if book_details is None: 
        return "404 error"
    else:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "UONdS2vRM5tHX06Yy4Hikg", "isbns": isbn})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']    
        result = {
        "title": book_details.title,
        "author": book_details.author,
        "year": book_details.year,
        "isbn": isbn,
        "review_count": work_ratings_count,
        "average_score":average_rating 
        }
        return jsonify(result)


@app.route("/logout") 
def logout():
   # remove the username from the session if it is there
   session.pop('login_id', None)
   return redirect(url_for('login'))


@app.route("/contact") 
def contact():
   return render_template("contact.html")



@app.route("/about") 
def about():
    if 'login_id' in session:
        return render_template("about.html",  login_id=session['login_id'])
    else:
        return 'You are not logged in'