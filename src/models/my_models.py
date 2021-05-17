from datetime import datetime

from src import db


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.DateTime, default=datetime.utcnow())
    salary = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    child = db.relationship('Employee', backref='dep')