import json
import gzip

# import mongoengine as mongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client['amazon_books']
# database = db['users']


with open('data/user_data.json') as f:
    n = 0
    for user in f:

        if n % 1000 == 0:
            print(user)

        data = json.loads(user)

        try:
            del data['_id']
        except KeyError:
            pass

        for book in data['books']:
            book['rating'] = int(book['rating']['$numberInt'])
            book['unix_review_time'] = int(book['unix_review_time']['$numberInt'])

        database.insert(data)

        n += 1


client.close()
