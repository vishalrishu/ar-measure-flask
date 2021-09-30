import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):    
    database_name ='flask_app'
    default_database_path= "postgresql://{}:{}@{}/{}".format('postgres', 'aaaa1111', 'localhost:5432', database_name)
    database_path = os.getenv('DATABASE_URL', default_database_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class Measure(db.Model):
    __tablename__='measures'

    id=db.Column(db.Integer, primary_key=True, unique=True)
    object_name=db.Column(db.String(120))
    object_width=db.Column(db.Numeric(12, 2))
    object_height=db.Column(db.Numeric(12, 2))
    object_area=db.Column(db.Numeric(12, 2))
    
    def __init__(self, object_name, object_height,object_width,object_area):
        self.object_name=object_name
        self.object_width=object_width
        self.object_height=object_height
        self.object_area=object_area

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80))
    email=db.Column(db.String(80), unique = True)
    password=db.Column(db.String(120))

    def __init__(self,name,email,password):
        self.name=name
        self.email=email
        self.password=password