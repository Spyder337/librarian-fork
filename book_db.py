#   Sql database
import sqlite3
from logging import Logger

conn_string: str = "data/isbn_database.db"

def create_table() -> None:
    """
        Creates a sqlite3 database if none exists.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS books
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT NOT NULL,
                    path TEXT NOT NULL,
                    title TEXT,
                    publishers TEXT,
                    pubDate TEXT);''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
        
def isbn_exists(isbn: str) -> bool:
    """Checks if an ISBN string exists in the database.

    Args:
        isbn (str): ISBN string to search for in DB.

    Returns:
        bool: Whether or not the ISBN exists.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()

    # Check if the ISBN exists in the database
    c.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
    result = c.fetchone()

    # Close the connection
    conn.close()

    return result is not None

def store_book(isbn: str, filePath: str, title: str = None, publishers: str = None, 
               publishDate: str = None, log: Logger = None):
    """
        Store a book and its metadata (optional).
    """

    if(isbn_exists(isbn)):
        return False
    conn = sqlite3.connect(conn_string)
    command = conn.cursor()
    
    command.execute(f"""INSERT 
                    INTO books (isbn, path, title, publishers, pubDate) 
                    VALUES ({isbn}, \"{filePath}\", \"{title}\", \"{publishers}\", \"{publishDate}\")""")
    conn.commit()
    conn.close()
    return True

def get_book(isbn: str, log: Logger = None) -> [str]:
    """
        Generates a list of book attributes if a book exists.
    Args:
        isbn (str): ISBN-13 of the book.

    Returns:
        [str]: List of ISBN, associated file name, title, publishers, and
        publishing date in that order.
    """
    if not isbn_exists(isbn):
        return None
    
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()
    vals: [str] = []
    try:
        c.execute(f"""SELECT * FROM books WHERE isbn={isbn}""")
        res = c.fetchone()
        vals = [res[1], res[2], res[3], res[4], res[5]]
    except:
        if not log == None:
            log.exception(f"Book not found in db: {isbn}")
            
    conn.close()
    return vals
    
def get_all_books(log: Logger = None) -> [[str]]:
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()
    
    try:
        c.execute(f"""SELECT * FROM books""")
        res = c.fetchall()
        books = []
        for b in res:
            books.append([b[1], b[2], b[3], b[4], b[5]])
            
        print(f"{'ISBN':14s}{'Title':100s}")
        for book in books:
            print(f"{book[0]:14s}{book[2]:100s}")
        #print(books)
        print()
    except:
        if not log == None:
            log.exception("Failed to request books from database.")
            
    conn.close()
    return books
    
def update_meta_data(isbn: str,
                   title: str, publishers: str,
                   publishDate: str, log: Logger = None):
    
    """
        Update a books metadata.
    """
    
    if isbn_exists(isbn):
        conn = sqlite3.connect(conn_string)
        c = conn.cursor()
        try:
            c.execute(f"""UPDATE books SET 
                      title=\"{title}\",
                      publishers=\"{publishers}\",
                      pubDate=\"{publishDate}\"
                      WHERE isbn={isbn};
                      """)
            conn.commit()
        except:
            if(log != None):
                log.exception(f"Failed to update book with isbn:{isbn}")
            return False
        conn.close()
        return True
    else:
        return False

def store_isbn(isbn: str, filePath: str, logger:Logger=None) -> bool:
    """
    

    Args:
        isbn (str): ISBN string for the book.
        filePath (str): Location of the eBook or barcode image.
        logger (Logger, optional): Log to write errors and exceptions to. Defaults to None.

    Returns:
        bool: Whether or not the book was stored sucessfully.
    """
    # Check if the ISBN already exists in the database
    if isbn_exists(isbn):
        return False
    # Connect to the SQLite database
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()
    #   Try to store the information in the db. Otherwise log the info. 
    try:
        # Insert the ISBN into the database
        c.execute(f"INSERT INTO books (isbn, path) VALUES ({isbn}, \"{filePath}\")")

        # Commit the changes and close the connection
        conn.commit()
    except:
        if logger != None:
            logger.exception(f"Failed to store {filePath} in db with ISBN: {isbn}")
    conn.close()

    return True