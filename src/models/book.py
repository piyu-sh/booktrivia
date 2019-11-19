from flask_restplus import fields
from server.instance import server
from server.instance import server

db = server.db

fact = server.api.model('Fact', {
    'id': fields.Integer(readonly=True),
    'fact_text': fields.String(description="fact text"),
    'book_id': fields.Integer(readonly=True)
})

book = server.api.model('Book', {
    'id': fields.Integer(readonly=True),
    'title': fields.String(required=True, min_length=1, max_length=200, description='Book title'),
    'imageURL': fields.String(description="url to fetch book cover"),
    'facts': fields.List(fields.Nested(fact))
})

class Books(db.Model):
    __tablename_ = 'Books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False )
    imageURL = db.Column(db.Text, nullable=True)
    facts = db.relationship('Facts', passive_deletes=True, backref=db.backref('books'))

class Facts(db.Model):
    __tablename_ = 'Facts'
    id = db.Column(db.Integer, primary_key=True)
    fact_text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id',  ondelete='CASCADE'))

db.create_all()
db.session.commit()