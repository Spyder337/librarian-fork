from collections import OrderedDict
import json
import requests

class OpenLibraryProvider:
    baseUrl: str = "https://openlibrary.org"
    
    def fetch_book(self, isbn: str):
        request_url = self.baseUrl + f"/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(request_url)
        if response.ok:
            data = response.json()
            root = ""
            for key in data:
                #print(key, ":", data[key])
                root = key
            pubData = self.merge_pub_data(data[root]["publishers"])
            return [data[root]["title"], pubData, data[root]["publish_date"]]
        return None
    
    def merge_pub_data(data):
        retStr = ""
        for item in data:
            retStr += (item["name"] + ";")
        return retStr