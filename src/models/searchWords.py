from flask_restplus import fields
from server.instance import server

db = server.db

searchWordsApiModel = server.api.model('Fact', {
    'id': fields.Integer(readonly=True),
    'keyword': fields.String(description="keyword or phrase"),
})

searchQueryApiModel = server.api.model('SearchQuery', {
    'searchQuery': fields.String(description="search query")
})

class SearchWordsDBModel(db.Model):
    __tablename__ = 'search_words'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.Text, unique=True, nullable=False )

db.create_all()
db.session.commit()