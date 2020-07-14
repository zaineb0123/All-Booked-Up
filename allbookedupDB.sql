CREATE TABLE books(
	book_id SERIAL PRIMARY KEY,
	isbn INTEGER, 
	title VARCHAR, 
	author VARCHAR, 
	year INTEGER
);

CREATE TABLE users (
	user_id SERIAL PRIMARY KEY,
	first_name VARCHAR NOT NULL,
	last_name VARCHAR NOT NULL,
	login_id VARCHAR NOT NULL,
	password VARCHAR NOT NULL
	
);

CREATE TABLE reviews(
	review_id SERIAL PRIMARY KEY,
	isbn INTEGER, 
	rating VARCHAR NOT NULL,
	review_description VARCHAR NOT NULL,
	review_date DATE NOT NULL DEFAULT CURRENT_DATE,
	book_id INTEGER,
	user_id INTEGER REFERENCES users
);