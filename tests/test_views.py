import http

from flask import request, get_flashed_messages

from src import app, db
from src.models.my_models import Department, Employee


class TestViews:
    temp_id_emp = 21
    temp_id_dep = 21

    def test_populate_db(self):
        id = 20
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + f'populate/{id}'
            resp = client.get(f'/populate/{id}', follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == f"DB successfully populated by {id} records"
        assert resp.status_code == http.HTTPStatus.OK
        TestViews.temp_id_emp = db.session.query(Employee).all()[-1].id
        TestViews.temp_id_dep = db.session.query(Department).all()[-1].id

    def test_populate_db_over_limit(self):
        id = 200000
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + f'populate/{id}'
            print('*' * 50, url)
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == f"DB not populated by {id} records, please request less 1000 records"
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/'
            resp = client.get(url)

        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_employees_with_db_between_dates(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            params = '?date_picker1=1985-07-22&date_picker2=1992-07-22'
            url = request.host_url[:-1] + ':5000/' + params
            resp = client.get(url)

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
            url = request.host_url[:-1] + ':5000/' + 'insert'
            client.post(url, data=data, follow_redirects=True)
            client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Inserted Successfully"
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
            url = request.host_url[:-1] + ':5000/' + f'update/{TestViews.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Updated Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_delete_view_employee_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + f'delete/{TestViews.temp_id_emp}'

            resp = client.post(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Employee Deleted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_view_departments_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments'
            resp = client.get(url)
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_view_department_with_db(self):
        data = {
            "name": "Fake Department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments/' + 'insert'
            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Inserted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_department_with_db(self):
        data = {
            "name": "New Department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments/' + f'update/{TestViews.temp_id_dep}'

            resp = client.post(url, data=data, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Updated Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_delete_view_department_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments/' + f'delete/{TestViews.temp_id_dep}'
            resp = client.post(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "Department Deleted Successfully"
        assert resp.status_code == http.HTTPStatus.OK

    def test_drop_all(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'drop-all'
            resp = client.get(url, follow_redirects=True)
            message = get_flashed_messages()

        assert message[0] == "DB successfully dropped"
        assert resp.status_code == http.HTTPStatus.OK
