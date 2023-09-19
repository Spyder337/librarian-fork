#!/usr/bin/env python3

import cv2
from pyzbar import pyzbar
import sqlite3
import os
import isbnlib
import time
import book_db
from book_meta import OpenLibraryProvider
from book_parser import validate_and_convert

class BarcodeScanner:
    book_detected: bool = False
    isbn_stored: bool = False
    barcode_detected: bool = False
    last_valid_isbn: str = None
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

    def store_isbn(self, isbn, frame):
        """
        Stores a new ISBN in the database and saves the associated frame in the
        captures directory.

        :param isbn: The ISBN to store.
        :param frame: The image frame containing the barcode.
        :return: True if the ISBN was stored successfully, False otherwise.
        """
        def_provider = OpenLibraryProvider
        framePath = f"captures/barcode_{isbn}.png"
        
        #   Fetch metadata for the newly found isbn.
        meta = def_provider.fetch_book(def_provider, isbn)
        if(meta != None):
            meta.path = framePath
            book_db.store_book(meta)
            #print(meta)
        else:
            #   If none is found just store the path to the image with the isbn
            book_db.store_isbn(isbn, framePath)
        
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

        # Save the frame as an image with the ISBN as the filename:
        filename = f"captures/barcode_{isbn}.png"
        cv2.imwrite(filename, frame)

    def capture_single_barcode(self):
        """
        Captures a single frame from the webcam, detects the barcode, and stores
        the valid ISBN in the database along with metadata if available.
        """
        cap = cv2.VideoCapture(0)
        
        ret, frame = cap.read()
        cv2.imshow('Barcode Scanner', frame)
        
        if not self.book_detected and not self.isbn_stored:
            barcodes = pyzbar.decode(frame)
            
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                if validate_and_convert(barcode_data) != None:
                    self.store_isbn(barcode_data, frame)
                    self.barcode_detected = True
                    self.last_valid_isbn = barcode_data
                    
            if self.barcode_detected == True:
                self.book_detected = True
                self.isbn_stored = True
            else:
                self.book_detected = False
                self.isbn_stored = False
                
            if self.barcode_detected:
                print("Valid ISBN barcode detected.")
                print("Last valid ISBN: ", self.last_valid_isbn)
            else:
                print("No valid ISBN barcode detected.")

            # Reset the barcode detection flag:
            self.barcode_detected = False
            
            time.sleep(1)
            cap.release()
            cv2.destroyAllWindows()

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
                    if validate_and_convert(barcode_data) != None:
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

    def start_scanning(self):
        """
        Initiates the barcode scanning process and captures ISBN barcodes from
        the webcam feed.
        """
        print("Barcode Scanner - Press 'q' or 'esc' to quit")

        # Capture barcodes and store ISBNs in the database:
        self.capture_barcode(self)
