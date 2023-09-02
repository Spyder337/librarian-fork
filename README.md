# librarian

A Python ISBN barcode scanner that uses a webcam feed and stores the ISBN numbers in an SQLite database. This README provides a detailed overview of the program's features, usage, and setup instructions.

## Features

- Real-time barcode scanning using a webcam feed
- Detection and storage of valid ISBN barcodes in an SQLite database
- Confirmation messages for successful barcode detection and storage
- Captured barcode frames saved as images in a 'captures' directory
- Validation of ISBN using the `isbnlib` library

## Prerequisites

Before using the Barcode Scanner program, ensure you have the following dependencies installed:

- Python 3.x
- OpenCV (`cv2`)
- `pyzbar` library
- `isbnlib` library
- SQLite3

You can install these dependencies using the following command:

```bash
pip install opencv-python pyzbar isbnlib
```

Usage

    Clone the repository to your local machine:

```bash
git clone <repository-url>
```

Navigate to the repository directory:

```bash
cd barcode-scanner-program
````

Run the barcode_scanner.py script:

```bash
python barcode_scanner.py
```

A webcam feed window will appear showing the camera's view. Slide books with ISBN barcodes underneath the camera to detect and store their ISBNs.

Press 'q' or 'esc' to quit the program and close the webcam feed window.

## Configuration

The program contains a few configuration options:

The program assumes a USB webcam is used, oriented facing your desk for easy barcode scanning.
You can change the location of the SQLite database file by modifying the database connection paths in the code.
Captured barcode frames are saved in a 'captures' directory. You can change this directory's name or location by modifying the save_capture function.

## Additional Notes

The BarcodeScanner class provides methods for creating the database table, checking for existing ISBNs, storing ISBNs, and more.
The is_valid_isbn method validates ISBNs using the isbnlib library, checking both ISBN-10 and ISBN-13 formats.
The capture_barcode method continuously captures frames, detects barcodes, and stores ISBNs until you exit the program.

## Contribution

Contributions to this project are welcome! If you encounter any issues, have ideas for improvements, or want to add new features, feel free to submit a pull request or open an issue.

## License

This barcode scanner is open-source and licensed under the MIT License. See the LICENSE file for more details.
