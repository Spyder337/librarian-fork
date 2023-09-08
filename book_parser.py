import os
from logging import Logger
from book_db import store_isbn, update_meta_data, store_book
from book_meta import OpenLibraryProvider
#   Libraries for finding and validating ISBNs
import isbnlib
import re
#   Libraries for OCR Pdfs
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
#   Library for Epub files
import ebooklib
from ebooklib import epub
#   Library for CHTML and parsing Epub text
from bs4 import BeautifulSoup
#   Library for Djvu files


#   Variables
isbnPattern = r"(\b978(?:-?\d){10}\b)|(\b978(?:-?\d){9}(?:-?X|x))|(\b(?:-?\d){10})\b|(\b(?:-?\d){9}(?:-?X|x)\b)"


def validate_and_convert(isbn: str) -> str | None:
    """
        Sanitizes then validates an isbn using isbnlib. If its isbn10 it is then converted
        to isbn13 and returned.
        
        Args:
            isbn (str): Isbn to be validated as a string.
            
        Returns:
            str | None: The valid isbn as an ISBN-13 or None if invalid.
    """
    isbn = isbn.replace("-", "").replace(" ", "")
    if (isbnlib.is_isbn10(isbn) | isbnlib.is_isbn13(isbn)):
        if(isbnlib.is_isbn10):
            isbn = isbnlib.to_isbn13(isbn)
        return isbn
    else:
        return None

#   Uses regex to find an isbn in text
#   Returns the first result or None
def find_isbn_in_text(text: str) -> str | None:
    """
        Uses Regex to parse text for a valid isbn string.

    Args:
        text (str): Text string to be parsed for a valid isbn.

    Returns:
        str | None: Either a valid isbn or None.
    """
    isbn = None
    match = re.search(isbnPattern, text)
    if (match != None):
        isbn = match.group()
        isbn = validate_and_convert(isbn)
    return isbn


def parse_isbn_from_pdf(fileName: str, numPages: int = 10) -> str | None:
    """
        Scans a pdf using OCR and regex for an ISBN.

    Args:
        fileName (str): Full filepath to the pdf.
        numPages (int, optional): Number of pages to scan by default. Defaults to 10.

    Returns:
        str | None: Either a valid ISBN or None.
    """
    isbn = None
    pdf_pages = convert_from_path(fileName, 200, last_page=numPages, thread_count=2)
    for i in range(numPages):
        page: Image = pdf_pages[i]
        text: str = pytesseract.image_to_string(page)
        isbn = find_isbn_in_text(text)
        if (isbn != None):
            break
    return isbn


def parse_isbn_from_epub(fileName: str) -> str | None:
    """
        Scans an epub using OCR and regex for an ISBN.
    Args:
        fileName (str): Full filepath to the file to be read.

    Returns:
        str | None: Either a valid isbn13 string or None.
    """
    isbn = None
    book = epub.read_epub(fileName, {"ignore_ncx": True})
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    text: [str] = []
    for chapter in items:
        soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
        #   Generate a list of paragraphs
        text = [para.get_text() for para in soup.find_all('p')]
        #   Join them into a single string
        for para in text:
            isbn = find_isbn_in_text(para)
            if isbn != None:
                return isbn
    return isbn

def parse_directories(dirPath: [str], logger: Logger) -> [str]:
    """
        Scan directories for valid eBooks and their ISBNs.

    Args:
        dirPath (str]): Directories to scan for eBooks.
        logger (Logger): Log that is written to.

    Returns:
        [str]: List of valid ISBNs found in the directories.
    """
    fileCount: int = 0
    epubCount: int = 0
    parsedEpubCount: int = 0
    pdfCount: int = 0
    parsedPdfCount: int = 0
    valid_isbns: [str] = []
    def_provider = OpenLibraryProvider
    
    for dir in dirPath:
        files = os.listdir(dir)
        for file in files:
            filePath = dir + "/" + file
            try:
                if file.endswith(".pdf"):
                    pdfCount += 1
                    fileCount += 1
                    isbn = parse_isbn_from_pdf(filePath)
                    if (isbn != None):
                        valid_isbns.append(isbn)
                        parsedPdfCount += 1
                        meta = def_provider.fetch_book(def_provider, isbn)
                        if(meta != None):
                            store_book(isbn, filePath, meta[0], meta[1], meta[2], logger)
                            #print(meta)
                        else:
                            store_isbn(isbn, filePath, logger)
                    else:
                        logger.error(f"Failed to parse \"{file}\"")
                        
                elif file.endswith(".epub"):
                    epubCount += 1
                    fileCount += 1
                    isbn = parse_isbn_from_epub(filePath)
                    if (isbn != None):
                        valid_isbns.append(isbn)
                        parsedEpubCount += 1
                        meta = def_provider.fetch_book(def_provider, isbn)
                        if(meta != None):
                            store_book(isbn, filePath, meta[0], meta[1], meta[2], logger)
                            #print(meta)
                        else:
                            store_isbn(isbn, filePath, logger)
                    else:
                        logger.error(f"Failed to parse \"{file}\"")
            
            except:
                logger.error(f"Failed to parse \"{file}\"")

    print(f"Parsed Pdfs: {parsedPdfCount} out of {pdfCount}")
    print(f"Parsed Epubs: {parsedEpubCount} out of {epubCount}")
    print(f"Successfully scanned {parsedPdfCount + parsedEpubCount} out of {fileCount} files in directory.")

    return valid_isbns
