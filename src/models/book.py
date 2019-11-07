from flask_restplus import fields
from server.instance import server
from server.instance import server

db = server.db

book = server.api.model('Book', {
    'title': fields.String(required=True, min_length=1, max_length=200, description='Book title'),
    'imageURL': fields.Url(description="url to fetch book cover"),
    'facts': fields.List(fields.String(description='fact'))
})

class Books(db.Model):
    __tablename_ = 'Books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False )
    imageURL = db.Column(db.Text, nullable=True)
    facts = db.relationship('Facts', backref=db.backref('books'))

class Facts(db.Model):
    __tablename_ = 'Facts'
    id = db.Column(db.Integer, primary_key=True)
    fact_text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

db.create_all()
db.session.commit()