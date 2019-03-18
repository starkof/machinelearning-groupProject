import mongoengine as mongo
from models import *


mongo.connect('amazon_books')

training = TrainingSet(userID='8888')
training.books = [Book(bookID='slfk485j', rating=3), Book(bookID='szzzz09v09', rating=4)]

training.save()

print(TrainingSet.objects)
