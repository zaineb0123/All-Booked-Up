        results = db.execute("SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author ", {"isbn" :bookSearch, "title" : bookSearch, "author" :bookSearch}).fetchone()
