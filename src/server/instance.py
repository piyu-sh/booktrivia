from flask import Flask
from flask_restplus import Api
from environment.instance import environment_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class Server(object):
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app, 
            version='1.0', 
            title='BookTrivia API',
            description='BookTrivia API', 
            doc = environment_config["swagger-url"]
        )
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.app.config['SQLALCHEMY_ECHO'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/booktrivia'
        self.db = SQLAlchemy(self.app)
        self.migrate = Migrate(self.app,self.db)

    def run(self):
        self.app.run(
                debug = environment_config["debug"], 
                port = environment_config["port"]
            )

server = Server()