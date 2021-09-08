import json
import random
from datetime import datetime
from faker import Faker

from requests.exceptions import Timeout

import requests

from flask import render_template, request, flash, url_for, redirect
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from src import app, db, logger

from src.models.my_models import Department, Employee
from src.service.service import DepartmentService


@app.route('/', methods=['GET'])
def index():
    """If User goes address '/' program will give him list of all employees.
    If User on page '/' pick dates and click choose he will see employees """
    if request.args.get('date_picker1') and request.args.get('date_picker2'):
        try:
            date1 = datetime.strptime(request.args.get('date_picker1'), '%Y-%m-%d').date()
            date2 = datetime.strptime(request.args.get('date_picker2'), '%Y-%m-%d').date()
        except ValueError as e:
            logger.debug(f"Value error for search Employees between dates is {e}")
            flash(f"{e}", "danger")
            return redirect(url_for('index'))
        if date1 > date2:
            logger.debug("Value error 'the first date must be less than the second'")
            flash("Value error 'the first date must be less than the second'", "danger")
            return redirect(url_for('index'))

        my_data = dict(date1=date1, date2=date2)
        url = request.host_url + 'json/employees'
        # logger.debug(url)
        # logger.debug(request.__dict__)
        # logger.debug(os.environ.__dict__)
        all_employees = requests.get(url, params=my_data, verify=False, allow_redirects=True)
        if all_employees.status_code == 200:
            flash(f"Employees successfully searched between dates {date1} and {date2}", "success")
        all_employees = all_employees.json()
    elif request.args.get('department_id'):
        department_id = request.args.get('department_id')
        my_data = dict(department_id=department_id)
        url = request.host_url + 'json/employees'
        all_employees = requests.get(url, params=my_data, verify=False, allow_redirects=True)
        if all_employees.status_code == 200:
            flash(f"Employees successfully selected by department", "success")
        all_employees = all_employees.json()
    else:
        all_employees = requests.get(request.host_url + 'json/employees', verify=False, allow_redirects=True).json()

    n_rows = request.args.get('rows') or 10
    if request.args.get('less'):
        n_rows = int(n_rows) - 10
    elif request.args.get('more'):
        n_rows = int(n_rows) + 10
    n_rows = max(int(n_rows), 10)

    return render_template("index.html", employee=all_employees[:n_rows], n_rows=n_rows)


@app.route('/insert', methods=['POST'])
def insert():
    """After click button 'Add New Employee' on page '/' user will see modal form with
    fields which need to fill. After click 'Add Employee' the record will be tried to post and user will see a message"""
    name = request.form['name']
    try:
        birthday = str(datetime.strptime(request.form['birthday'], '%Y-%m-%d').date())
        if int(birthday[:4]) not in range(1900, 2015):
            raise ValueError("date must be in range between dates 1900-01-01 and 2015-01-01")
    except ValueError as e:
        logger.debug(f"Value error for insert Employee in field birthday is {e}")
        flash(f"{e}", "danger")
        return redirect(url_for('index'))
    salary = request.form['salary']
    if not salary.isdigit():
        logger.debug("Value error for insert Employee in field salary")
        flash("Value error for insert Employee in field salary", "danger")
        return redirect(url_for('index'))
    department_name = request.form['department_name']
    if not all([name, department_name]):
        logger.debug("Validation error, fields name or department are empty")
        flash("Validation error, fields name or department are empty", "danger")
    my_data = json.dumps(dict(name=name, birthday=birthday, salary=salary, department_name=department_name))

    headers = {'Content-type': 'application/json'}
    url = request.host_url + 'json/employees'
    rq = requests.post(url, headers=headers, data=my_data, verify=False, allow_redirects=True)
    if rq.status_code == 400:
        flash(rq.json()['message'], 'danger')
    if rq.status_code == 201:
        flash("Employee Inserted Successfully", "success")
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    """After click button 'edit' on page 'employees' user will see modal form with fields specified record .
    After click update the record will try to update and user will be redirected to page '/' and will see a message"""
    if request.method == 'POST':
        name = request.form['name']
        try:
            birthday = str(datetime.strptime(request.form['birthday'], '%Y-%m-%d').date())
        except ValueError as e:
            logger.debug(f"Value error for update Employee in field birthday is {e}")
            flash(f"{e}", "danger")
            return redirect(url_for('index'))
        salary = request.form['salary']
        if not salary.isdigit():
            logger.debug("Value error for update Employee in field salary")
            flash("Value error for update Employee in field salary", "danger")
            return redirect(url_for('index'))
        department_name = request.form['department_name']
        if not all([name, department_name]):
            logger.debug("Validation error, fields name or department are empty")
            flash("Validation error, fields name or department are empty", "danger")

        my_data = json.dumps(dict(id=id, name=name, birthday=birthday, salary=salary, department_name=department_name))

        headers = {'Content-type': 'application/json'}
        url = request.host_url + 'json/employees/' + str(id)
        rq = requests.patch(url, headers=headers, data=my_data, verify=False, allow_redirects=True)
        if rq.status_code == 200:
            flash("Employee Updated Successfully", "success")

        return redirect(url_for('index'))


@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    """After click button delete on page 'employees'
    the specified record will try to delete and user will see a message"""
    url = request.host_url + 'json/employees/' + str(id)
    rq = requests.delete(url, verify=False, allow_redirects=True)

    if rq.status_code == 204:
        flash("Employee Deleted Successfully", "success")

    return redirect(url_for('index'))


@app.route('/departments', methods=['GET'])
def departments():
    """If User goes address '/departments' program will give him list of departments with which Employees were binded"""
    headers = {'Content-type': 'application/json'}

    url = request.host_url + 'json/departments'
    params = {"field": request.args.get("field", "id"), "ordr": request.args.get("ordr", "desc")}
    rq = requests.get(url, headers=headers, params=params, verify=False, allow_redirects=True)
    return render_template("departments.html", departments=rq.json())


@app.route('/departments/insert', methods=['POST'])
def department_insert():
    """After click button 'Add New Department' on page 'departments' user will see modal form with
    fields which need to fill. After click 'Add Department' the record will be tried to post and user will see a message"""
    name = request.form['name']
    if not name:
        logger.debug("Validation error, field name must not be empty")
        flash("Validation error, field name must not be empty", "danger")

    my_data = json.dumps(dict(name=name))

    headers = {'Content-type': 'application/json'}
    url = request.host_url + 'json/departments'
    rq = requests.post(url, headers=headers, data=my_data, verify=False, allow_redirects=True)
    if rq.status_code == 409:
        flash(rq.json()['message'], 'danger')
    if rq.status_code == 201:
        flash("Department Inserted Successfully", "success")
    return redirect(url_for('departments'))


@app.route('/departments/update/<int:id>', methods=['POST'])
def department_update(id):
    """After click button edit on page 'departments' user will see modal form with specified record fields.
    After click update the record will be tried to update and user will see a message"""
    name = request.form['name']
    if not name:
        logger.debug("Validation error, field name must not be empty")
        flash("Validation error, field name must not be empty", "danger")

    my_data = json.dumps(dict(id=id, name=name))

    headers = {'Content-type': 'application/json'}
    url = request.host_url + 'json/departments/' + str(id)
    rq = requests.put(url, headers=headers, data=my_data, verify=False, allow_redirects=True)
    if rq.status_code == 200:
        flash("Department Updated Successfully", "success")
    return redirect(url_for('departments'))


@app.route('/departments/delete/<int:id>', methods=['GET'])
def department_delete(id):
    """After click button delete on page 'departments'
    the specified record will be tried to delete and user will see a message"""
    url = request.host_url + 'json/departments/' + str(id)
    rq = requests.delete(url, verify=False, allow_redirects=True)
    if rq.status_code == 204:
        flash("Department Deleted Successfully", "success")

    return redirect(url_for('departments'))


@app.route('/populate/<int:id>', methods=['GET'])
def populate_db(id):
    """User can get address like /populate/23, where 23 is arbitrary number of new fake Employees.
        After this request DB will be updated with new records"""

    if id > 1000:
        flash(f"DB not populated by {id} records, please request less 1000 records", "danger")
        return redirect(url_for('index'))

    fake = Faker()
    employees_to_create = []
    for _ in range(id):
        data = {
            "name": fake.name(),
            "birthday": str(fake.date_between_dates(date_start=datetime(1985, 1, 1),
                                                    date_end=datetime(2000, 1, 1))),
            "salary": random.randrange(100, 5000, 100),
            "department_name": random.choice(['web', 'frontend', 'backend', 'simulations',
                                              'graphic', 'android', 'iOS', 'ml', 'ds', 'marketing'])
        }
        department = DepartmentService.fetch_department_by_name(db.session, name=data["department_name"])

        if not department:
            department = Department(name=data["department_name"])
            db.session.add(department)
            db.session.commit()

        employees_to_create.append(Employee(name=data["name"], birthday=data["birthday"],
                                            salary=data["salary"], department_id=department.id))

    db.session.bulk_save_objects(employees_to_create)
    db.session.commit()
    flash(f"DB successfully populated by {id} records", "success")
    return redirect(url_for('index'))


@app.route('/populate2/<int:id>', methods=['GET'])
def populate_db2(id):
    """User can get address like /populate2/4, where 4 is arbitrary number of new fake Employees.
    After this request DB will be updated with new records.
    But instead of populate_db version 1 this algorithm uses rest web-services 'post',
    not directly getting access with DB"""
    if id > 1000:
        flash(f"DB not populated by {id} records, please request less 1000 records", "danger")
        return redirect(url_for('index'))

    fake = Faker()
    all_dicts = []
    for _ in range(id):
        new_dict = {
            "name": fake.name(),
            "birthday": str(fake.date_between_dates(date_start=datetime(1985, 1, 1),
                                                    date_end=datetime(2000, 1, 1))),
            "salary": random.randrange(100, 5000, 100),
            "department_name": random.choice(['web', 'frontend', 'backend', 'simulations',
                                              'graphic', 'android', 'iOS', 'ml', 'ds', 'marketing'])
        }
        all_dicts.append(new_dict)
    my_data = json.dumps(all_dicts)
    headers = {'Content-type': 'application/json'}
    url = request.host_url + 'json/employees'
    rq = requests.post(url, headers=headers, params={"populate": True}, data=my_data, verify=False,
                       allow_redirects=True)
    if rq.status_code == 201:
        flash(f"DB successfully populated by {id} records", "success")
    return redirect(url_for('index'))


@app.route('/drop-all', methods=['GET'])
def drop_db():
    """After get address /drop-all DB will be erased from data"""
    if request.method == 'GET':
        db.drop_all()
        db.create_all()
        flash('DB successfully dropped', "success")
    return redirect(url_for('index'))
