from mongoengine import *


class Book(EmbeddedDocument):
    bookID = StringField()
    rating = IntField()


class User(Document):
    userID = StringField(required=True)
    books = ListField(EmbeddedDocumentField(Book))

    meta = {'allow_inheritance': True}


class TrainingSet(User):
    pass


class TestingSet(User):
    pass


class TuningSet(User):
    pass
