from flask import render_template, request, flash, url_for, redirect
from sqlalchemy import func

from src import db, app, api
from src.models.my_models import Employee, Department
from src.rest.empl import EmployeeListApi


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
    #print(all_data)

    return render_template("departments.html", departments=all_data)


api.add_resource(EmployeeListApi, '/employees', '/employees/<uuid>', strict_slashes=False)