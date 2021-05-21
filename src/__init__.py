import logging

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = "Secret Key"

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/finalproject2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/finalproject'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bbdd61c5c0e309:14359da5@eu-cdbr-west-01.cleardb.com/heroku_49c300e9821f2bb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logger = logging.getLogger('app_logger')
logger.setLevel('DEBUG')

std_format = logging.Formatter(fmt='{asctime} - {levelname} - {name} - {message}', style='{')

file_handler = logging.FileHandler('debug.log')
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
logger.addHandler(file_handler)

console_handler.setFormatter(std_format)
file_handler.setFormatter(std_format)

db = SQLAlchemy(app)

api = Api(app)

migrate = Migrate(app, db)

"""
after changes in terminal you need:
flask db init
flask db migrate
flask db upgrade

to see strings not covered
coverage run -m pytest --cov=src --cov-report term-missing
"""

from src.models import my_models
from src.views import my_views
from src.rest import empl, schemas

db.create_all()
