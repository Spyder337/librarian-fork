import json
import requests

class OpenLibraryProvider:
    baseUrl: str = "https://openlibrary.org"
    
    def fetchBook(self, isbn: str) -> requests.Response:
        request_url = self.baseUrl + f"/api/books?bibkeys=ISBN:{isbn}&&callback=mycallback"
        response = requests.get(request_url)
        for key in response:
            print(key, ":", response[key])
        return response