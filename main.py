import os
import platform
import logging
from pathlib import Path
from book_parser import parseDirectories
from book_db import create_table
from book_meta import OpenLibraryProvider
from librarian import BarcodeScanner

#   Example of guards for output
#   Gets the path for the books to be scanned
if platform.system() == "Windows":
    root_dir = Path("~\Desktop").expanduser()
else:
    root_dir = Path("~").expanduser()

#   Default path to books
booksDir = root_dir / Path("Books")

#   Path to store the log file
parser_log_path: str = "logs/parser.log"

def initFolders() -> None:
    #   Create the logs and data directory if none exists
    if(not os.path.exists("logs")):
        os.makedirs("logs")
    if(not os.path.exists("data")):
        os.makedirs("data")
    # Create the captures directory if it doesn't exist:
    if not os.path.exists('captures'):
        os.makedirs('captures')
        
def initLogging() -> logging.Logger:
    logging.basicConfig(filename=parser_log_path, filemode='w', format="%(levelname)s:%(asctime)s - %(message)s")
    logger=logging.getLogger()
    return logger

def getBooksDir() -> str:
    inputdir = input("Input a path to parse or leave blank for default:")
    if(inputdir == ""):
        inputdir = booksDir
    return inputdir

def main():
    initFolders()
    #   Create the database for isbns and books
    create_table()
    log = initLogging()
    print("[1] Scan barcodes")
    print("[2] Scan folder")
    print("[3] Exit")
    in_val = input()
    if in_val == "1":
        scanner = BarcodeScanner
        scanner.start_scanning(self=scanner)
    elif in_val == "2":
        #   Get the root dir to search for books
        bookDir = getBooksDir()
        parseDirectories([x[0] for x in os.walk(bookDir)], log)
    else:
        quit()
        
if __name__ == "__main__":
    main()