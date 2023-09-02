#!/usr/bin/env python3

import cv2
from pyzbar import pyzbar
import sqlite3
import os
import isbnlib
import time

class BarcodeScanner:
    """
    This class represents a barcode scanner that captures ISBN barcodes from a
    webcam feed and stores them in a SQLite database.

    Note: I recommend a USB webcam that is oriented facing your desk so you
    can slide books one after another underneath the camera to rapidly
    catelogue barcodes.
    """
    def __init__(self):
        """
        Initializes the BarcodeScanner instance with various flags and
        attributes.
        """
        self.book_detected = False
        self.isbn_stored = False
        self.barcode_detected = False
        self.last_valid_isbn = None

    def create_table(self):
        """
        Creates a table named 'books' in the SQLite database to store ISBNs.
        """
        # Connect to the SQLite database:
        conn = sqlite3.connect('isbn_database.db')
        c = conn.cursor()

        # Create the table if it doesn't exist:
        c.execute('''CREATE TABLE IF NOT EXISTS books
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     isbn TEXT NOT NULL);''')

        # Commit the changes and close the connection:
        conn.commit()
        conn.close()

    def isbn_exists(self, isbn):
        """
        Checks if a given ISBN already exists in the database.

        :param isbn: The ISBN to check.
        :return: True if the ISBN exists, False otherwise.
        """
        # Connect to the SQLite database:
        conn = sqlite3.connect('isbn_database.db')
        c = conn.cursor()

        # Check if the ISBN exists in the database:
        c.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        result = c.fetchone()

        # Close the connection:
        conn.close()

        return result is not None

    def store_isbn(self, isbn, frame):
        """
        Stores a new ISBN in the database and saves the associated frame in the
        captures directory.

        :param isbn: The ISBN to store.
        :param frame: The image frame containing the barcode.
        :return: True if the ISBN was stored successfully, False otherwise.
        """
        # Check if the ISBN already exists in the database:
        if self.isbn_exists(isbn):
            print("ISBN already exists in the database.")
            return False

        # Connect to the SQLite database:
        conn = sqlite3.connect('isbn_database.db')
        c = conn.cursor()

        # Insert the ISBN into the database:
        c.execute("INSERT INTO books (isbn) VALUES (?)", (isbn,))

        # Commit the changes and close the connection:
        conn.commit()
        conn.close()

        # Save the frame in the captures directory:
        self.save_capture(frame, isbn)

        return True

    def save_capture(self, frame, isbn):
        """
        Saves an image frame to the 'captures' directory using the ISBN in the
        filename.

        :param frame: The image frame to save.
        :param isbn: The ISBN used as the filename.
        """
        # Create the captures directory if it doesn't exist:
        if not os.path.exists('captures'):
            os.makedirs('captures')

        # Save the frame as an image with the ISBN as the filename:
        filename = f"captures/barcode_{isbn}.png"
        cv2.imwrite(filename, frame)

    def capture_barcode(self):
        """
        Captures frames from the webcam, detects barcodes, and stores valid
        ISBNs in the database.
        """
        # Open the webcam:
        cap = cv2.VideoCapture(0)

        while True:
            # Read a frame from the webcam:
            ret, frame = cap.read()

            # Pause for 1 second after the frame is read:
            time.sleep(1)

            # Display the frame:
            cv2.imshow('Barcode Scanner', frame)

            # Find and decode barcodes if a new book is detected and not yet
            # stored:
            if not self.book_detected and not self.isbn_stored:
                barcodes = pyzbar.decode(frame)

                # If a barcode is detected, filter and store the ISBN:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    if self.is_valid_isbn(barcode_data):
                        self.store_isbn(barcode_data, frame)
                        self.barcode_detected = True
                        self.last_valid_isbn = barcode_data
                        break

            # Set the flags based on barcode detection:
            if self.barcode_detected:
                self.book_detected = True
                self.isbn_stored = True
            else:
                self.book_detected = False
                self.isbn_stored = False

            # Show the confirmation message:
            if self.barcode_detected:
                print("Valid ISBN barcode detected.")
                print("Last valid ISBN: ", self.last_valid_isbn)
            else:
                print("No valid ISBN barcode detected.")

            # Reset the barcode detection flag:
            self.barcode_detected = False

            # Check for 'q' or 'esc' key to exit:
            if cv2.waitKey(1) in (ord('q'), 27):
                break

        # Release the webcam:
        cap.release()
        cv2.destroyAllWindows()

    def is_valid_isbn(self, isbn):
        """
        Checks if a given string is a valid ISBN.

        :param isbn: The ISBN string to check.
        :return: True if the ISBN is valid, False otherwise.
        """
        # Remove any hyphens or spaces from the ISBN:
        isbn = isbn.replace("-", "").replace(" ", "")

        # Check if the ISBN is valid using isbnlib:
        return isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn)

    def start_scanning(self):
        """
        Initiates the barcode scanning process and captures ISBN barcodes from
        the webcam feed.
        """
        print("Barcode Scanner - Press 'q' or 'esc' to quit")

        # Create the table in the database if it doesn't exist:
        self.create_table()

        # Capture barcodes and store ISBNs in the database:
        self.capture_barcode()

if __name__ == "__main__":
    scanner = BarcodeScanner()
    scanner.start_scanning()
