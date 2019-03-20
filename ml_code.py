import numpy as np
from models import *
import mongoengine as mongo
import json
from time import time
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metric

mongo.connect('amazon_books')


def create_book_and_user_indexes(maximum):
    book_ids = {}
    user_ids = {}

    print('initializing')
    n = 0
    for user in Users.objects[:maximum]:
        user_ids[user.user_id] = len(user_ids)

        for book in user.books:
            if n % 1000 == 0:
                print(book.book_id)
            if book.book_id not in book_ids:
                book_ids[book.book_id] = len(book_ids)

            n += 1

    books = json.dumps(book_ids)
    users = json.dumps(user_ids)

    with open('book_indexes.json', 'w') as f:
        print(books, file=f)

    with open('user_indexes.json', 'w') as f:
        print(users, file=f)


def create_sparse_matrix():

    with open('book_indexes.json') as f:
        book_indexes = json.loads(f.read())
    with open('user_indexes.json') as f:
        user_indexes = json.loads(f.read())

    with open('data/sparse_matrix.csv', 'w') as f:
        n = 0
        for user in user_indexes:
            line = [0] * len(book_indexes)

            if len(line) != 6457:
                print(line)
                print(len(line))
                print()

            for book in Users.objects(user_id=user)[0].books:
                if book.rating > 3:
                    line[book_indexes[book.book_id]] = 1

            if n % 1000 == 0:
                print(line)

            print(','.join(str(c) for c in line), file=f)
            n += 1


def svd_sparse_matrix(max_rows):
    t = time()
    print('reading sparse matrix')
    matrix = np.genfromtxt('data/sparse_matrix.csv', delimiter=',', max_rows=max_rows)
    print(matrix)
    print('reading time ->', time()-t)

    t = time()
    print('performing svd')
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    print('svd time ->', time()-t)

    print(u.shape)
    print(u)
    print()

    print(u.shape)
    print(s)
    print()

    print(u.shape)
    print(vh)

    return u, s, vh


def train():
    samples = 2000
    print('initializing')
    mlp = MLPClassifier(solver='sgd', hidden_layer_sizes=(1, 1), activation='relu',
                        learning_rate='adaptive', max_iter=500)

    print('fetching data')
    y_data = np.genfromtxt('data/sparse_matrix.csv', delimiter=',', max_rows=samples)

    y_train = y_data[:(samples//2)]
    y_test = y_data[(samples//2):]

    del y_data

    print('performing svd')
    x_train, s, vh = np.linalg.svd(y_train, full_matrices=False)
    x_test, s, vh = np.linalg.svd(y_test, full_matrices=False)

    print('training')
    mlp.fit(x_train, y_train)

    print('predicting')
    y_pred = mlp.predict(x_test)
    print([i for i in y_pred[:1]])

    accuracy = metric.accuracy_score(np.array(y_test).flatten(), np.array(y_pred).flatten(), normalize=True)
    fmeasure = metric.f1_score(y_test.flatten(), y_pred.flatten(), average='weighted')

    print('accuracy =', accuracy)
    print('fmeasure =', fmeasure)


if __name__ == '__main__':
    # sparse_matrix()
    # create_book_and_user_indexes(20000)
    # create_sparse_matrix()
    # svd_sparse_matrix()
    train()
