from src import db


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, index=True, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, name, birthday, salary, department_id=None):
        self.name = name
        self.birthday = birthday
        self.salary = salary
        self.department_id = department_id

    def __repr__(self):
        return f'Employee({self.id}, {self.name}, {self.birthday}, {self.salary}, {self.department_id})'


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    child = db.relationship('Employee', backref='dep_record')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Department({self.id}, {self.name}, {self.child})'

