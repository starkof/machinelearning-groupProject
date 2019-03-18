from mongoengine import *


class Book(EmbeddedDocument):
    book_id = StringField()
    rating = IntField()
    unix_review_time = IntField()


class Users(Document):
    user_id = StringField(required=True)
    books = ListField(EmbeddedDocumentField(Book))

    meta = {'allow_inheritance': True}


class BookReviews(DynamicDocument):
    meta = {
        'collection': 'book_reviews'
    }

    reviewerID = StringField()
    asin = StringField()
    helpful = ListField(IntField())
    overall = IntField()
    unixReviewTime = IntField()
    reviewTime = StringField()


class TrainingSet(Users):
    pass


class TestingSet(Users):
    pass


class TuningSet(Users):
    pass
