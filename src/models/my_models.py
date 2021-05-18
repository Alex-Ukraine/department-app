from datetime import datetime

from src import db


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.Date, index=True, nullable=False)
    salary = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __repr__(self):
        return f'Employee({self.id}, {self.name}, {self.birthday}, {self.salary}, {self.department_id})'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    child = db.relationship('Employee', backref='dep')

    def __repr__(self):
        return f'Department({self.id}, {self.name}, {self.child})'

