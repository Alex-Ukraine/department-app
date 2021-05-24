from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

import logging.config

from settings import logger_config

app = Flask(__name__)
app.secret_key = "Secret Key"

#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/finalproject"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b28bfef9567dc7:4956928b@eu-cdbr-west-01.cleardb.com/heroku_380d0cff17aa9f2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

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
