from flask import Flask
from flask_restplus import Api, Resource, fields

from server.instance import server
from models.book import book, Books, Facts

from werkzeug.exceptions import BadRequest
from flask import abort

app, api, db = server.app, server.api, server.db

# Let's just keep them in memory 
books_db = [
    {"id": 0, "title": "War and Peace"},
    {"id": 1, "title": "Python for Dummies"},
]

# This class will handle GET and POST to /books
@api.route('/books')
class BookList(Resource):
    @api.marshal_list_with(book)
    def get(self):
        return Books.query.all()

    # Ask flask_restplus to validate the incoming payload
    @api.expect(book, validate=True)
    @api.marshal_with(book)
    def post(self):
        newBook = Books(title = api.payload.get('title'), imageURL=api.payload.get('imageURL'))
        for fact in api.payload.get('facts'):
            newBook.facts.append(Facts(fact_text = fact.get('fact_text')))
        db.session.add(newBook)
        db.session.commit()
        return newBook



# Handles GET and PUT to /books/:id
# The path parameter will be supplied as a parameter to every method
@api.route('/books/<int:id>')
class Book(Resource):
    @api.marshal_with(book)
    def get(self, id):
        # match = self.find_one(id)
        return Books.query.filter(Books.id==id).first()

    def delete(self, id):
        match = Books.query.filter(Books.id==id)
        response = match.first()
        if response is None:
            raise BadRequest('id not present')
        match.delete()
        db.session.commit()
        return True


    # Ask flask_restplus to validate the incoming payload
    @api.expect(book, validate=True)
    @api.marshal_with(book)
    def put(self, id):
        match = self.find_one(id)
        if match != None:
            match.update(api.payload)
            match["id"] = id
        return match