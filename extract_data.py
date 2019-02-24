import json
import gzip

# import mongoengine as mongo
from pymongo import MongoClient


# mongo.connect('amazon_books.book_reviews')


client = MongoClient('localhost', 27017)
db = client['amazon_books']
database = db['book_reviews']


def parse(path):
    g = gzip.open(path, 'r')

    for i in g:
        yield json.dumps(eval(i))


n = 0
for l in parse("data/reviews_Books.json.gz"):

    if n % 1000 == 0:
        print(l)

    data = json.loads(l)

    try:
        del data['reviewerName']
        del data['reviewText']
        del data['summary']
    except KeyError:
        pass

    database.insert(data)
    # print(data)

    n += 1


client.close()
