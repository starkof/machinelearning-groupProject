import numpy as np
from models import *
import mongoengine as mongo

mongo.connect('amazon_books')


def create_sparse_matrix(start, stop):
    book_ids = {}
    user_ids = []

    print('initializing')
    n = 0
    for user in Users.objects[start:stop]:
        user_ids.append(user.user_id)

        for book in user.books:
            if n % 1000 == 0:
                print(book.book_id)
            if book.book_id not in book_ids:
                book_ids[book.book_id] = len(book_ids)

            n += 1

    with open('data/sparse_matrix.csv', 'a') as f:
        n = 0
        for user in user_ids:
            line = ['0'] * len(book_ids)

            for book in Users.objects(user_id=user)[0].books:
                if book.rating > 3:
                    line[book_ids[book.book_id]] = '1'

            if n % 1000 == 0:
                print(line)

            print(','.join(line), file=f)
            n += 1


def sparse_matrix():
    count = Users.objects.count()

    page_size = 1000
    page_number = 1

    while True:
        start = (page_number - 1) * page_size
        end = (page_number * page_size)

        if end < count:
            create_sparse_matrix(start, end)
        else:
            create_sparse_matrix(start, count-1)
            break

        page_number += 1


if __name__ == '__main__':
    sparse_matrix()
