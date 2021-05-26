import http

import requests
from flask import request, get_flashed_messages

from src import app, db
from src.models.my_models import Department, Employee


class TestViews:
    temp_id_emp = 21
    temp_id_dep = 21
    port = ''

    #port = ':5000'

    def test_populate_db(self):
        id = 20
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'populate/{id}'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

            s = request.host, request.environ['RAW_URI'], request.full_path, request.environ['REQUEST_URI']
            assert s == ''

        assert message[0] == f"DB successfully populated by {id} records"
        assert resp.status_code == http.HTTPStatus.OK
        TestViews.temp_id_emp = db.session.query(Employee).all()[-1].id
        TestViews.temp_id_dep = db.session.query(Department).all()[-1].id

    def test_populate_db_over_limit(self):
        id = 200000
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'populate/{id}'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == f"DB not populated by {id} records, please request less 1000 records"
        assert resp.status_code == http.HTTPStatus.OK

    def test_populate_db2(self):
        id = 2
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'populate2/{id}'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == f"DB successfully populated by {id} records"
        assert resp.status_code == http.HTTPStatus.OK

    def test_populate_db2_over_limit(self):
        id = 200000
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'populate2/{id}'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == f"DB not populated by {id} records, please request less 1000 records"
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/'
            resp = client.get(url)
        assert resp.status_code == http.HTTPStatus.OK

    # *********************************************

    def test_get_view(self):
        with app.test_request_context('/'), \
                app.test_client():
            url = request.host_url
            resp = requests.get(url, verify=False)

        assert resp.status_code == http.HTTPStatus.OK

    # *********************************************

    def test_get_view_employees_with_db_between_dates(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            params = '?date_picker1=1985-07-22&date_picker2=1992-07-22'
            url = request.host_url[:-1] + f'{TestViews.port}/' + params
            resp = client.get(url, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db_selected_department_id(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            params = '?department_id=1'
            url = request.host_url[:-1] + f'{TestViews.port}/' + params
            resp = client.get(url, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db_between_dates_date1_bigger_date2(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            params = '?date_picker1=1997-07-22&date_picker2=1992-07-22'
            url = request.host_url[:-1] + f'{TestViews.port}/' + params
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Value error 'the first date must be less than the second'"
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db_between_dates_bad_data(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            params = '?date_picker1=19850722&date_picker2=19920722'
            url = request.host_url[:-1] + f'{TestViews.port}/' + params
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "time data '19850722' does not match format '%Y-%m-%d'"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1990-11-11",
            "salary": 789,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Inserted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db_data_not_valid(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1990.11.11",
            "salary": 789,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "time data '1990.11.11' does not match format '%Y-%m-%d'"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db_data_out_of_range(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1900-11-11",
            "salary": 789,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Validation error to post Employee {'birthday': ['birthday must be greater than 1930.']}"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db_data_out_of_range_on_form(self):
        data = {
            "name": "Fake Employee",
            "birthday": "2016-11-11",
            "salary": 789,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "date must be in range between dates 1900-01-01 and 2015-01-01"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db_fields_empty(self):
        data = {
            "name": "",
            "birthday": "1990-11-11",
            "salary": 789,
            "dep": " "
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Validation error, fields name or department are empty"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_employee_with_db_salary_not_valid(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1990-11-11",
            "salary": "wer122",
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Value error for insert Employee in field salary"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_employee_with_db(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1989-06-10",
            "salary": 785,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'update/{TestViews.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Updated Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_employee_with_db_date_no_valid(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1989.06.10",
            "salary": 785,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'update/{TestViews.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "time data '1989.06.10' does not match format '%Y-%m-%d'"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_employee_with_db_salary_not_valid(self):
        data = {
            "name": "Fake Employee",
            "birthday": "1989-06-10",
            "salary": 'ert',
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'update/{TestViews.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Value error for update Employee in field salary"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_employee_with_db_fields_are_empty(self):
        data = {
            "name": " ",
            "birthday": "1989-06-10",
            "salary": '123',
            "dep": ""
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'update/{TestViews.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Validation error, fields name or department are empty"
        assert resp.status_code == http.HTTPStatus.OK

    def test_delete_view_employee_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + f'delete/{TestViews.temp_id_emp}'

            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Deleted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_departments_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments'
            resp = client.get(url)
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_department_with_db(self):
        data = {
            "name": "Fake Department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments/' + 'insert'
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Inserted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_department_with_db_empty_field(self):
        data = {
            "name": ""
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments/' + 'insert'
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Validation error, field name must not be empty"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_department_with_db(self):
        data = {
            "name": "New Department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments/' + f'update/{TestViews.temp_id_dep}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Updated Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_department_with_db_empty_field(self):
        data = {
            "name": ""
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments/' + f'update/{TestViews.temp_id_dep}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Validation error, field name must not be empty"
        assert resp.status_code == http.HTTPStatus.OK
        TestViews.temp_id_dep = db.session.query(Department).all()[-1].id

    def test_delete_view_department_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'departments/' + f'delete/{TestViews.temp_id_dep}'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Deleted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_drop_all(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + f'{TestViews.port}/' + 'drop-all'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "DB successfully dropped"
        assert resp.status_code == http.HTTPStatus.OK
