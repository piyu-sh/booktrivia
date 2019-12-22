from flask import Flask
from flask_restplus import Resource, fields, Namespace, marshal

from server.instance import server
from models.book import Books
from models.searchWords import SearchWordsDBModel, searchQueryApiModel
from werkzeug.exceptions import BadRequest
from flask import abort
from sqlalchemy import func
app, api, db = server.app, server.api, server.db

searchQueryApiNS = Namespace('searchQuery', description='book title + search word = search query')
api.add_namespace(searchQueryApiNS)

# This class will handle GET to /searchQuery
@searchQueryApiNS.route('/')
class SearchQueryList(Resource):

    @searchQueryApiNS.marshal_list_with(searchQueryApiModel)
    def get(self):
        seach_query = func.concat(Books.title," ", SearchWordsDBModel.keyword)
        result = (db.session.query(seach_query.label("searchQuery"))).select_from(Books, SearchWordsDBModel).all()        
        return [{'searchQuery': row.searchQuery} for row in result]

