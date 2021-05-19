import json
import os
import random
from datetime import datetime
from faker import Faker

import requests

from flask import render_template, request, flash, url_for, redirect

from src import app, db
import urllib.request

from src.models.my_models import Department, Employee
from src.rest.schemas import EmployeeSchema, DepartmentSchema_Without_Id
from src.service.service import DepartmentService


@app.route('/', methods=['GET'])
def index():
    if request.args.get('date_picker1') and request.args.get('date_picker2'):
        my_data = dict(date1=request.args.get('date_picker1'), date2=request.args.get('date_picker2'))
        url = request.host_url + 'json/employees'
        all_employees = requests.get(url, params=my_data, verify=False).json()
    else:
        all_employees = requests.get(request.host_url + 'json/employees').json()
    return render_template("index.html", employee=all_employees)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        birthday = str(datetime.strptime(request.form['birthday'], '%d.%m.%Y').date())
        salary = request.form['salary']
        dep = request.form['dep']
        my_data = json.dumps(dict(name=name, birthday=birthday, salary=salary, dep=dep))

        headers = {'Content-type': 'application/json'}
        url = request.host_url + 'json/employees'
        rq = requests.post(url, headers=headers, data=my_data, verify=False)
        if rq.status_code == 201:
            flash("Employee Inserted Successfully")
        return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        salary = request.form['salary']
        dep = request.form['dep']

        my_data = json.dumps(dict(id=id, name=name, birthday=birthday, salary=salary, dep=dep))

        headers = {'Content-type': 'application/json'}
        url = request.host_url + 'json/employees/' + str(id)
        rq = requests.patch(url, headers=headers, data=my_data, verify=False)
        if rq.status_code == 200:
            flash("Employee Updated Successfully")

        return redirect(url_for('index'))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    url = request.host_url + 'json/employees/' + str(id)
    rq = requests.delete(url, verify=False)

    if rq.status_code == 204:
        flash("Employee Deleted Successfully")

    return redirect(url_for('index'))


@app.route('/departments')
def departments():
    headers = {'Content-type': 'application/json'}

    url = request.host_url + 'json/departments'
    rq = requests.get(url, headers=headers, verify=False)

    return render_template("departments.html", departments=rq.json())


@app.route('/departments/insert', methods=['POST'])
def department_insert():
    if request.method == 'POST':
        name = request.form['name']

        my_data = json.dumps(dict(name=name))

        headers = {'Content-type': 'application/json'}
        url = request.host_url + 'json/departments'
        rq = requests.post(url, headers=headers, data=my_data, verify=False)
        if rq.status_code == 201:
            flash("Department Inserted Successfully")
        return redirect(url_for('departments'))


@app.route('/departments/update/<int:id>', methods=['GET', 'POST'])
def department_update(id):
    if request.method == 'POST':
        name = request.form['name']

        my_data = json.dumps(dict(id=id, name=name))

        headers = {'Content-type': 'application/json'}
        url = request.host_url + 'json/departments/' + str(id)
        rq = requests.patch(url, headers=headers, data=my_data, verify=False)

        if rq.status_code == 200:
            flash("Department Updated Successfully")

        return redirect(url_for('departments'))


@app.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
def department_delete(id):
    url = request.host_url + 'json/departments/' + str(id)
    rq = requests.delete(url)
    if rq.status_code == 204:
        flash("Department Deleted Successfully")

    return redirect(url_for('departments'))


@app.route('/populate/<int:id>', methods=['GET'])
def populate_db(id):
    if request.method == 'GET':
        fake = Faker()
        for _ in range(id):
            data = {
                "name": fake.first_name(),
                "birthday": str(fake.date_between_dates(date_start=datetime(1985, 1, 1),
                                                        date_end=datetime(2000, 1, 1))),
                "salary": random.randrange(100, 5000, 100),
                "dep": random.choice(['web', 'frontend', 'backend', 'simulations',
                                      'graphic', 'android', 'iOS', 'ml', 'ds', 'marketing'])
            }
            department = DepartmentService.fetch_department_by_name(db.session, name=data["dep"])

            if not department:
                department = Department(name=data["dep"])
                db.session.add(department)
                db.session.commit()

            employee = Employee(name=data["name"], birthday=data["birthday"],
                                salary=data["salary"], department_id=department.id)
            db.session.add(employee)
        db.session.commit()

        return {"message": f"DB successfully populated by {id} records"}, 200
