from flask import Flask
from flask_restplus import Resource, fields, Namespace

from server.instance import server
from models.book import bookWithFacts, bookWithoutFacts, fact, Books, Facts

from werkzeug.exceptions import BadRequest
from flask import abort

app, api, db = server.app, server.api, server.db

factsApi = Namespace('facts', description='urls for fact related operations')
api.add_namespace(factsApi)

# This class will handle GET and POST to /facts/book/:id
@factsApi.route('/book/<int:id>')
class BookList(Resource):

    @factsApi.doc(description='fetch all facts corresponding to a book id')
    @factsApi.marshal_list_with(fact)
    def get(self, id):
        return Facts.query.filter(Facts.book_id==id).all()


# Handles GET, DELETE and PUT to /facts/:id
# The path parameter will be supplied as a parameter to every method
@factsApi.route('/<int:id>')
class Fact(Resource):
    @factsApi.marshal_with(fact)
    def get(self, id):
        match = Facts.query.filter(Facts.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        return match

    def delete(self, id):
        match = Facts.query.filter(Facts.id==id)
        response = match.first()
        if response is None:
            raise BadRequest('id not present')
        match.delete()
        db.session.commit()
        return True


    # Ask flask_restplus to validate the incoming payload
    @factsApi.expect(fact, validate=True)
    @factsApi.marshal_with(fact)
    def put(self, id):
        match = Facts.query.filter(Facts.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        match.fact_text = factsApi.payload.get('fact_text')
        db.session.commit()
        return match