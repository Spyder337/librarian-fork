from collections import OrderedDict
import json
import requests
from book import Book

class OpenLibraryProvider:
    baseUrl: str = "https://openlibrary.org"
    
    def fetch_book(self, isbn: str) -> Book:
        """
            Fetches a book from OpenLibrary's api.
        Args:
            isbn (str): Book's isbn as a string.

        Returns:
            [str]: List containing title, publishers, and publish date.
        """
        request_url = self.baseUrl + f"/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(request_url)
        if response.ok:
            data = response.json()
            root = ""
            for key in data:
                #print(key, ":", data[key])
                root = key
            pubData = self.merge_pub_data(data[root]["publishers"])
            b = Book(data[root]["title"], isbn, pubData, data[root]["publish_date"])
            return b
        return None
    
    def merge_pub_data(data) -> str:
        """_summary_

        Args:
            data : Publisher data as returned by the OpenLibrary api call.

        Returns:
            str: String containing all publisher names deliniated by a ';'.
        """
        retStr = ""
        for item in data:
            retStr += (item["name"] + ";")
        return retStr