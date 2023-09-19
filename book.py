class Book:
    title: str
    isbn: str
    publishers: str
    publish_date: str
    path: str
    
    def __init__(self) -> None:
        pass
    
    def __init__(self, title: str, isbn: str, publishers: str, publish_date: str, path: str = ""):
        self.title = title
        self.isbn = isbn
        self.publishers = publishers
        self.publish_date = publish_date
        self.path = path