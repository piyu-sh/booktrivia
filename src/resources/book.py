from flask import Flask
from flask_restplus import Resource, fields, Namespace

from server.instance import server
from models.book import bookWithFacts, bookWithoutFacts, fact, Books, Facts

from werkzeug.exceptions import BadRequest
from flask import abort

app, api, db = server.app, server.api, server.db

booksApi = Namespace('books', description='urls for book related operations')
api.add_namespace(booksApi)

# This class will handle GET and POST to /books
@booksApi.route('/')
class BookList(Resource):
    @booksApi.marshal_list_with(bookWithFacts)
    def get(self):
        return Books.query.all()

    # Ask flask_restplus to validate the incoming payload
    @booksApi.expect(bookWithFacts, validate=True)
    @booksApi.marshal_with(bookWithFacts)
    def post(self):
        newBook = Books(title = booksApi.payload.get('title'), imageURL=booksApi.payload.get('imageURL'))
        for fact in booksApi.payload.get('facts'):
            newBook.facts.append(Facts(fact_text = fact.get('fact_text')))
        db.session.add(newBook)
        db.session.commit()
        return newBook



# Handles GET, DELETE and PUT to /books/:id
# The path parameter will be supplied as a parameter to every method
@booksApi.route('/<int:id>')
class Book(Resource):
    @booksApi.marshal_with(bookWithFacts)
    def get(self, id):
        match = Books.query.filter(Books.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        return match

    def delete(self, id):
        match = Books.query.filter(Books.id==id)
        response = match.first()
        if response is None:
            raise BadRequest('id not present')
        match.delete()
        db.session.commit()
        return True


    # Ask flask_restplus to validate the incoming payload
    @booksApi.expect(bookWithoutFacts, validate=True)
    @booksApi.marshal_with(bookWithFacts)
    def put(self, id):
        match = Books.query.filter(Books.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        match.title = booksApi.payload.get('title')
        match.imageURL=booksApi.payload.get('imageURL')
        db.session.commit()
        return match
