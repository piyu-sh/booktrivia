from flask_restplus import fields
from server.instance import server

book = server.api.model('Book', {
    'id': fields.Integer(description='Id'),
    'title': fields.String(required=True, min_length=1, max_length=200, description='Book title'),
    'imageURL': fields.Url(description="url to fetch book cover"),
    'facts': fields.List(fields.String(description='fact'))
})
