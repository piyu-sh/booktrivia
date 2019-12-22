from flask import Flask
from flask_restplus import Resource, fields, Namespace

from server.instance import server
# from models.book import bookWithFacts, bookWithoutFacts, fact, Books, Facts
from models.searchWords import SearchWordsDBModel, searchWordsApiModel
from werkzeug.exceptions import BadRequest
from flask import abort

app, api, db = server.app, server.api, server.db

searchWordsApiNS = Namespace('searchWord', description='search words to be added to book titles to create search queries')
api.add_namespace(searchWordsApiNS)

# This class will handle GET and POST to /searchWord
@searchWordsApiNS.route('/')
class SearchWordList(Resource):

    @searchWordsApiNS.marshal_list_with(searchWordsApiModel)
    def get(self):
        return SearchWordsDBModel.query.all()

    # Ask flask_restplus to validate the incoming payload
    @searchWordsApiNS.expect(searchWordsApiModel, validate=True)
    @searchWordsApiNS.marshal_with(searchWordsApiModel)
    def post(self):
        newSearchWord = SearchWordsDBModel(keyword =searchWordsApiNS.payload.get('keyword'))
        db.session.add(newSearchWord)
        db.session.commit()
        return newSearchWord

# Handles GET, DELETE and PUT to /searchWord/:id
# The path parameter will be supplied as a parameter to every method
@searchWordsApiNS.route('/<int:id>')
class SearchWord(Resource):
    @searchWordsApiNS.marshal_with(searchWordsApiModel)
    def get(self, id):
        match = SearchWordsDBModel.query.filter(SearchWordsDBModel.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        return match

    def delete(self, id):
        match = SearchWordsDBModel.query.filter(SearchWordsDBModel.id==id)
        response = match.first()
        if response is None:
            raise BadRequest('id not present')
        match.delete()
        db.session.commit()
        return True


    # Ask flask_restplus to validate the incoming payload
    @searchWordsApiNS.expect(searchWordsApiModel, validate=True)
    @searchWordsApiNS.marshal_with(searchWordsApiModel)
    def put(self, id):
        match = SearchWordsDBModel.query.filter(SearchWordsDBModel.id==id).first()
        if match is None:
            raise BadRequest('id not present')
        match.keyword = searchWordsApiNS.payload.get('keyword')
        db.session.commit()
        return match