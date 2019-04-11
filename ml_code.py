import numpy as np
from models import *
import mongoengine as mongo
import json
from time import time
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metric

mongo.connect('amazon_books')

# labels
# books the user liked = 1
# books the user has not read = 0
# books the user did not like = -1


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

    # books = json.dumps(book_ids)
    # users = json.dumps(user_ids)

    with open('book_indexes.csv', 'w') as f:
        for b in book_ids:
            print(','.join([b, str(book_ids[b])]), file=f)

    with open('user_indexes.csv', 'w') as f:
        for u in user_ids:
            print(','.join([u, str(user_ids[u])]), file=f)


def load_indexes(filename):
    indexes = {}

    with open(filename) as f:
        for line in f:
            line = line.rstrip().split(',')
            indexes[line[0]] = int(line[1])

    return indexes


def create_sparse_matrix():

    book_indexes = load_indexes('book_indexes.csv')
    user_indexes = load_indexes('user_indexes.csv')

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
                elif book.rating <= 3:
                    line[book_indexes[book.book_id]] = -1

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


def run_model():
    samples = 10
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
    print('xtrain')
    print(x_train)
    print()

    print('s')
    print(s)
    print()

    print('vh')
    print(vh)
    print()

    print('y_train')
    print(y_train)
    print()

    print()
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
    run_model()
