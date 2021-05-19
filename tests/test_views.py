import http
from dataclasses import dataclass
from unittest.mock import patch

from flask import request

from src import app, db
from src.models.my_models import Department, Employee


class TestViews:
    temp_id_emp = db.session.query(Employee).all()[-1].id

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
            "birthday": "11.11.1990",
            "salary": 789,
            "dep": "some_department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'insert'
            resp = client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)
            resp = client.post(url, data=data, follow_redirects=True)

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
            url = request.host_url[:-1] + ':5000/' + f'update/{self.temp_id_emp}'

            resp = client.post(url, data=data, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    def test_delete_view_employee_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + f'delete/{self.temp_id_emp}'

            resp = client.post(url, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    temp_id_dep = db.session.query(Department).all()[-1].id

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

        assert resp.status_code == http.HTTPStatus.OK

    def test_patch_view_department_with_db(self):
        data = {
            "name": "New Department"
        }
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments/' + f'update/{self.temp_id_dep}'

            resp = client.post(url, data=data, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    def test_delete_view_department_with_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'departments/' + f'delete/{self.temp_id_dep}'

            resp = client.post(url, follow_redirects=True)

        assert resp.status_code == http.HTTPStatus.OK

    def test_populate_db(self):
        with app.test_request_context('/'), \
                app.test_client() as client:
            url = request.host_url[:-1] + ':5000/' + 'populate/3'
            resp = client.get(url)

        assert resp.status_code == http.HTTPStatus.OK
