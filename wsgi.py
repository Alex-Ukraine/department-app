from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate, MigrateCommand


from flask import render_template, request, flash, url_for, redirect
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/finalproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

"""
after changes in terminal you need:
flask db init
flask db migrate
flask db upgrade
"""


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


@app.route('/')
def index():
    all_data = Employee.query.all()

    return render_template("index.html", employee=all_data)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        salary = request.form['salary']

        if not Department.query.filter_by(name=request.form['department']).first():
            db.session.add(Department(name=request.form['department']))
            db.session.commit()

        my_data = Employee(name=name, birthday=birthday, salary=salary,
                           dep=Department.query.filter_by(name=request.form['department']).first())
        db.session.add(my_data)
        db.session.commit()

        flash("Employee Inserted Successfully")

        return redirect(url_for('index'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Employee.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.birthday = request.form['birthday']
        my_data.salary = request.form['salary']

        if not Department.query.filter_by(name=request.form['department']).first():
            db.session.add(Department(name=request.form['department']))
            db.session.commit()
        my_data.dep = Department.query.filter_by(name=request.form['department']).first()

        db.session.commit()
        flash("Employee Updated Successfully")

        return redirect(url_for('index'))


@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    my_data = Employee.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Employee Deleted Successfully")

    return redirect(url_for('index'))


@app.route('/departments')
def departments():
    all_data = db.session.query(Employee.department_id, Department.name,
                                func.avg(Employee.salary).label('avg')).group_by(Employee.department_id).join(
        Department)
    print(all_data)

    return render_template("departments.html", departments=all_data)



if __name__ == "__main__":
    app.run(debug=True)