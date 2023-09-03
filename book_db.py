#   Sql database
import sqlite3
from logging import Logger

conn_string: str = "data/isbn_database.db"

def create_table() -> None:
    # Connect to the SQLite database
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS books
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT NOT NULL,
                    path TEXT NOT NULL);''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
        
def isbn_exists(isbn: str) -> bool:
    # Connect to the SQLite database
    conn = sqlite3.connect(conn_string)
    c = conn.cursor()

    # Check if the ISBN exists in the database
    c.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
    result = c.fetchone()

    # Close the connection
    conn.close()

    return result is not None
    
def store_isbn(isbn: str, filePath: str, logger:Logger=None) -> bool:
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