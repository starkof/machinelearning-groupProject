import numpy as np
from models import *
import mongoengine as mongo
import json
from time import time
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metric
import random

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
    n_users = 0
    for user in Users.objects.all():

        if len(user.books) > 2:
            n_users += 1
            print(user.id, len(user.books))

            user_ids[user.user_id] = len(user_ids)

            for book in user.books:
                if n % 1000 == 0:
                    print(book.book_id)

                if book.book_id not in book_ids:
                    book_ids[book.book_id] = len(book_ids)

                n += 1

        if n_users == maximum:
            break

    # books = json.dumps(book_ids)
    # users = json.dumps(user_ids)

    with open('book_indexes.txt', 'w') as f:
        for b in book_ids:
            print(','.join([b, str(book_ids[b])]), file=f)

    with open('user_indexes.txt', 'w') as f:
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

    book_indexes = load_indexes('book_indexes.txt')
    user_indexes = load_indexes('user_indexes.txt')

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
                    line[book_indexes[book.book_id]] = 0

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


def run_model(max_users=10):
    book_indexes = load_indexes('book_indexes.txt')
    user_indexes = load_indexes('user_indexes.txt')

    sparse_matrix = np.genfromtxt('data/sparse_matrix.csv', delimiter=',')

    u, s, x_data = np.linalg.svd(sparse_matrix, full_matrices=False)

    print('sparse_matrix')
    print(sparse_matrix.shape)
    print(sparse_matrix)
    print()

    user_models = {}

    k = 0
    for user_id in user_indexes:
        if k == max_users:
            break

        k += 1

        mlp = MLPClassifier(solver='sgd', hidden_layer_sizes=(10, 10), activation='relu',
                                learning_rate='adaptive', max_iter=5000)

        user = Users.objects(user_id=user_id)[0]

        training_books = []
        training_ratings = []

        testing_books = []
        testing_ratings = []

        n = 0
        for book in user.books:
            book_position = book_indexes[book.book_id]
            user_position = user_indexes[user.user_id]

            book_column = x_data[:, book_position]

            book_column = book_column * s

            # print(f'book position = {book_position}, user position = {user_position}')

            data_len = len(user.books)

            if n > data_len//2:
                training_books.append(list(book_column))
                training_ratings.append(sparse_matrix[user_position, book_position])
            else:
                testing_books.append(list(book_column))
                testing_ratings.append(sparse_matrix[user_position, book_position])

            n += 1

            # print('book column')
            # print(book_column, book_position)
            # print()

        training_books = np.array(training_books)
        training_ratings = np.array(training_ratings)

        # print('book ratings')
        # print(training_ratings)
        # print()
        #
        # print('reduced books')
        # print(training_books)
        # print()

        mlp.fit(training_books, training_ratings)

        # print('predictions probabilities')
        # print(mlp.predict_proba(testing_books))

        print('testing ratings')
        print(testing_ratings)

        print('predictions')
        predicted_ratings = mlp.predict(testing_books)
        print(predicted_ratings)

        accuracy = metric.accuracy_score(predicted_ratings, testing_ratings)
        fmeasure = metric.f1_score(predicted_ratings, testing_ratings)
        print(f'accuracy = {accuracy}')
        print(f'f-measure = {fmeasure}')
        print()
        print()

        user_models[user.user_id] = mlp

        # print(user.books)


if __name__ == '__main__':
    # sparse_matrix()
    # create_book_and_user_indexes(1000)
    # create_sparse_matrix()
    # svd_sparse_matrix(10)
    run_model()
