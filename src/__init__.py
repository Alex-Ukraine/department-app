from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = "Secret Key"

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/finalproject'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b3c78ba57ebdd1:4db201e9@eu-cdbr-west-01.cleardb.com/heroku_4ae52d2d28ec59f'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

migrate = Migrate(app, db)

"""
after changes in terminal you need:
flask db init
flask db migrate
flask db upgrade
"""

from src.models import my_models
from src.views import my_views
