import random
import numpy as np
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as metric


filename = 'sparse_matrix.csv'


# def hold_out(vector):
#     held_out = ['0'] * len(vector)
#
#      for b in vector:
#         if b == '1':
#             if random.random() < 0.5:
#                 pass


def generate_data(n_users):
    print('generating random data')
    categories = ['fiction', 'action', 'science', 'romance']

    book_indexes = {}

    # create books
    n = 0
    for c in categories:
        for i in range(1, 5):
            book_indexes[c + str(i)] = n
            n += 1

    # create users
    with open('sparse_matrix.csv', 'w') as f:
        book_keys = book_indexes.keys()

        for i in range(n_users):
            favorite = random.choice(categories)
            user_vector = ['0'] * len(book_indexes)

            for b in book_keys:

                if favorite in b:
                    if random.random() < 0.7:
                        user_vector[book_indexes[b]] = '1'
                    # if random.random() < 0.05:
                    #     user_vector[book_indexes[b]] = '-1'
                else:
                    if random.random() < 0.05:
                        user_vector[book_indexes[b]] = '1'
                    # if random.random() < 0.1:
                    #     user_vector[book_indexes[b]] = '-1'

            print(','.join(user_vector), file=f)
            print(favorite)
            print(user_vector)
            print()


def svd_sparse_matrix(filename):
    print('reading sparse matrix')
    matrix = np.genfromtxt(filename, delimiter=',')
    print(matrix)

    print('performing svd')
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)

    print(u.shape)
    print(u)
    print()

    print(u.shape)
    print(s)
    print()

    print(u.shape)
    print(vh)

    return u, s, vh


def show_data(filename):
    with open(filename) as f:
        print(f.read())


def run_model(svd_output, filename):
    samples = 50

    print('initializing')
    mlp = MLPClassifier(solver='sgd', hidden_layer_sizes=(700, 700, 700), activation='relu',
                        learning_rate='adaptive', max_iter=100000)

    print('fetching data')
    y_data = np.genfromtxt(filename, delimiter=',', max_rows=samples)

    y_train = y_data[(samples//2):]
    y_test = y_data[:(samples//2)]

    del y_data

    print('performing svd')
    X, s, vh = svd_output

    x_train = X[:(samples//2)]

    print()
    x_test, s, vh = np.linalg.svd(y_test, full_matrices=False)

    print('training')
    print('x_size', x_train.shape)
    print('y_size', y_test.shape)

    mlp.fit(x_train, y_train)

    print('predicting')
    y_pred = mlp.predict(x_test)
    print([i for i in y_pred[:1]])

    print('predictions')
    print(y_pred)

    # accuracy = metric.accuracy_score(np.array(y_test).flatten(), np.array(y_pred).flatten(), normalize=True)
    accuracy = np.mean(np.equal(y_test.flatten(), y_pred.flatten()))
    fmeasure = metric.f1_score(y_test.flatten(), y_pred.flatten(), average='weighted')

    print('accuracy =', accuracy)
    print('fmeasure =', fmeasure)


generate_data(100)
svd = svd_sparse_matrix(filename)
run_model(svd, filename)

show_data(filename)
