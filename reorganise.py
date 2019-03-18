# Reorganise the review data into user data

import mongoengine as mongo
from models import *


mongo.connect('amazon_books')


def doc_page():
    """
    Memory efficient generator to access to all data in the database using
    paging
    :return:
    """

    doc_count = BookReviews.objects.count()
    page_size = 100
    print('doc count ->', doc_count)

    page_number = 1
    while True:
        start = (page_number - 1)*page_size
        end = (page_number * page_size)

        if end < doc_count:
            yield BookReviews.objects[start:end]
        else:
            yield BookReviews.objects[start:]

        page_number += 1


def main():
    i = 0
    for reviews in doc_page():

        if i % 2000 == 0:
            print(i)

        for rev in reviews:
            if not Users.objects(user_id__exact=rev.reviewerID):
                book = Book(book_id=rev.asin, rating=rev.overall, unix_review_time=rev.unixReviewTime)

                user = Users(user_id=rev.reviewerID, books=[book])
                user.save()

            else:
                book = Book(book_id=rev.asin, rating=rev.overall, unix_review_time=rev.unixReviewTime)

                user = Users.objects(user_id=rev.reviewerID)
                user.update(add_to_set__books=[book])

            i += 1


if __name__ == '__main__':
    main()
