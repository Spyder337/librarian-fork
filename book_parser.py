import os
from logging import Logger
from book_db import storeIsbn, updateMetaData, store_book
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

"""
    Sanitizes then validates an isbn using isbnlib. If its isbn10 it is then converted
    to isbn13 and returned.
"""
def validateAndConvert(isbn: str) -> str | None:
        isbn = isbn.replace("-", "").replace(" ", "")
        if (isbnlib.is_isbn10(isbn) | isbnlib.is_isbn13(isbn)):
            if(isbnlib.is_isbn10):
                isbn = isbnlib.to_isbn13(isbn)
            return isbn
        else:
            return None

#   Uses regex to find an isbn in text
#   Returns the first result or None
def findIsbnInText(text: str) -> str | None:
    isbn = None
    match = re.search(isbnPattern, text)
    if (match != None):
        isbn = match.group()
        isbn = validateAndConvert(isbn)
    return isbn

"""
    Uses pytesseract to scan the first numPages of a pdf. If no isbn is found
    then none is returned.
"""
def parseIsbnFromPdf(fileName: str, numPages: int = 10) -> str | None:
    isbn = None
    pdf_pages = convert_from_path(fileName, 200, last_page=numPages, thread_count=2)
    for i in range(numPages):
        page: Image = pdf_pages[i]
        text: str = pytesseract.image_to_string(page)
        isbn = findIsbnInText(text)
        if (isbn != None):
            break
    return isbn

"""
    Reads an epub and regexes for potential isbn numbers and returns a valid one.
"""
def parseIsbnFromEpub(fileName: str) -> str | None:
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
            isbn = findIsbnInText(para)
            if isbn != None:
                return isbn
    return isbn

#   Scans books in supplied directories
def parseDirectories(dirPath: [str], logger: Logger) -> [str]:
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
                    isbn = parseIsbnFromPdf(filePath)
                    if (isbn != None):
                        valid_isbns.append(isbn)
                        parsedPdfCount += 1
                        meta = def_provider.fetchBook(def_provider, isbn)
                        if(meta != None):
                            store_book(isbn, file, meta[0], meta[1], meta[2], logger)
                            #print(meta)
                        else:
                            storeIsbn(isbn, file, logger)
                    else:
                        logger.error(f"Failed to parse \"{file}\"")
                        
                elif file.endswith(".epub"):
                    epubCount += 1
                    fileCount += 1
                    isbn = parseIsbnFromEpub(filePath)
                    if (isbn != None):
                        valid_isbns.append(isbn)
                        parsedEpubCount += 1
                        meta = def_provider.fetchBook(def_provider, isbn)
                        if(meta != None):
                            store_book(isbn, file, meta[0], meta[1], meta[2], logger)
                            #print(meta)
                        else:
                            storeIsbn(isbn, file, logger)
                    else:
                        logger.error(f"Failed to parse \"{file}\"")
            
            except:
                logger.error(f"Failed to parse \"{file}\"")

    print(f"Parsed Pdfs: {parsedPdfCount} out of {pdfCount}")
    print(f"Parsed Epubs: {parsedEpubCount} out of {epubCount}")
    print(f"Successfully scanned {parsedPdfCount + parsedEpubCount} out of {fileCount} files in directory.")

    return valid_isbns
