import os
import csv

from flask import Flask, session
from flask import render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['DATABASE_URL'] = "postgres://nfsspsyiahwqcm:b48f99892e6cb2abe36ed571f673cef2997deb4f1d25da8fe571f283d62ec0f5@ec2-23-20-129-146.compute-1.amazonaws.com:5432/d7d6t9lfnshmas"


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    print("i am in main, running")
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        print("title")
        print("author")
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()
    return "OK"

if __name__ == '__main__':
    main()