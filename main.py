import os
import platform
import logging
from logging import Logger
from pathlib import Path
from book_parser import parse_directories
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

def init_folders() -> None:
    #   Create the logs and data directory if none exists
    if(not os.path.exists("logs")):
        os.makedirs("logs")
    if(not os.path.exists("data")):
        os.makedirs("data")
    # Create the captures directory if it doesn't exist:
    if not os.path.exists('captures'):
        os.makedirs('captures')
        
def init_logs() -> Logger:
    logging.basicConfig(filename=parser_log_path, filemode='w', format="%(levelname)s:%(asctime)s - %(message)s")
    logger=logging.getLogger()
    return logger

def get_books_dir() -> str:
    inputdir = input("Input a path to parse or leave blank for default:")
    if(inputdir == ""):
        inputdir = booksDir
    return inputdir

def print_menu():
    print("""[1] Scan barcode
          [2] Scan barcodes
          [3] Scan folder
          [4] Scan Folders
          [5] Any other key""")

def parse_selection(log: Logger):
    sel = input()
    if sel == "1":
        scanner = BarcodeScanner
        scanner.capture_single_barcode(scanner)
    elif sel == "2":
        scanner = BarcodeScanner
        scanner.start_scanning(self=scanner)
    elif sel == "3":
        bookDir = get_books_dir()
        parse_directories([x[0] for x in os.walk(bookDir)], log)
    elif sel == "4":
        dirs = []
        print("Enter in directories seperated by pressing the return key.")
        print("Enter 'q' to quit.")
        while True:
            d = input("Directory Path: ")
            if (os.path.exists(d) and os.path.isdir(d)):
                dirs.append(d)
            elif d == "q":
                break                
            else:
                print("Invalid directory entered. Please try a valid one.")
        all_dirs = []
        for d in dirs:
            sub_dirs = [x[0] for x in os.walk(d)]
            for sd in sub_dirs:
                all_dirs.append(sd)
        parse_directories(all_dirs, log)
    else:
        quit()

def main():
    init_folders()
    #   Create the database for isbns and books
    create_table()
    #   Initialize the log for all files
    log = init_logs()
    while True:
        #   Print the selections
        print_menu()
        #   Get the user input
        parse_selection(log)
        
if __name__ == "__main__":
    main()