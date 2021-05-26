import http
import json
from dataclasses import dataclass
import random
from unittest.mock import patch

from src import app, db
from src.models.my_models import Department


@dataclass
class FakeDepartment:
    name = 'Fake Department'


class TestRestDepartments:
    db.create_all()
    id = []

    def test_populate_db(self):
        client = app.test_client()
        client.get('/populate/20')

    def test_get_departments_with_db(self):
        client = app.test_client()
        resp = client.get('/json/departments')

        assert resp.status_code == http.HTTPStatus.OK

    def test_get_departments_with_db_no_id_404(self):
        client = app.test_client()
        resp = client.get(f'/json/departments/{str(id(random.randint(1000, 2000)))}')

        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_get_departments_mock_db(self):
        with patch('src.service.service.DepartmentService.fetch_all_departments_with_avg_salary', autospec=True) \
                as mock_db_call:
            client = app.test_client()
            resp = client.get(f'/json/departments')

            mock_db_call.assert_called_once()
            assert resp.status_code == http.HTTPStatus.OK

    def test_create_department_with_db(self):
        client = app.test_client()
        data = {
            "name": "Fake Department"
        }
        resp = client.post('/json/departments', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.CREATED
        assert resp.json["name"] == "Fake Department"
        self.id.append(resp.json['id'])

    def test_create_department_with_db_error_validation_400(self):
        client = app.test_client()
        data = {
            "name": "Fake Department",
            "mood": "crazy"
        }
        resp = client.post('/json/departments', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_create_department_with_db_error_not_unique_409(self):
        client = app.test_client()
        data = {
            "name": "Fake Department"
        }
        resp = client.post('/json/departments', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.CONFLICT

    def test_get_department_by_id_with_db(self):
        client = app.test_client()
        resp = client.get(f'/json/departments/{self.id[0]}')

        assert resp.status_code == http.HTTPStatus.OK

    def test_create_department_with_mock_db(self):
        with patch('src.db.session.add', autospec=True) as mock_session_add, \
                patch('src.db.session.commit', autospec=True) as mock_session_commit:
            client = app.test_client()
            data = {
                "name": "Test Department"
            }
            resp = client.post('/json/departments', data=json.dumps(data), content_type='application/json')
            mock_session_add.assert_called_once()
            mock_session_commit.assert_called_once()

    def test_put_department_with_db(self):
        client = app.test_client()
        url = f"/json/departments/{self.id[0]}"
        data = {
            "name": "Update Name"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK
        assert resp.json["name"] == 'Update Name'

    def test_put_department_with_db_name_already_exists(self):
        client = app.test_client()

        data1 = {
            "name": "Fake Employee",
            "birthday": "1990-03-05",
            "salary": 1000,
            "dep": "frontend123"
        }
        client.post('/json/employees', data=json.dumps(data1), content_type='application/json')
        client.post('/json/employees', data=json.dumps(data1), content_type='application/json')

        url = f"/json/departments/{db.session.query(Department).all()[-4].id}"
        data2 = {
            "name": "frontend123"
        }
        resp = client.put(url, data=json.dumps(data2), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK

    def test_put_department_with_db_no_dep_404(self):
        client = app.test_client()
        url = "/json/departments/356345646346"
        data = {
            "name": "Update Name"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_update_department_with_db_no_dep_404(self):
        client = app.test_client()
        url = "/json/departments/356345646346"
        data = {
            "name": "Update Name"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_put_department_with_db_validation_error_400(self):
        client = app.test_client()
        url = f"/json/departments/{db.session.query(Department).all()[-1].id}"
        data = {
            "name": "Fake Department",
            "mood": "uneasy"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_update_department_with_mock_db(self):
        with patch('src.service.service.DepartmentService.fetch_department_by_id') as mocked_query, \
                patch('src.db.session.add', autospec=True) as mock_session_add, \
                patch('src.db.session.commit', autospec=True) as mock_session_commit:
            mocked_query.return_value = FakeDepartment()
            client = app.test_client()
            url = f'/json/departments/{self.id[0]}'
            data = {
                "name": "Fake Department"
            }
            resp = client.put(url, data=json.dumps(data), content_type='application/json')
            mock_session_add.assert_called_once()
            mock_session_commit.assert_called_once()

    def test_delete_department_with_db(self):
        client = app.test_client()
        url = f'/json/departments/{db.session.query(Department).all()[-1].id}'
        resp = client.delete(url)
        assert resp.status_code == http.HTTPStatus.NO_CONTENT

    def test_delete_department_with_db_no_such_id_404(self):
        client = app.test_client()
        url = '/json/departments/666666666666'
        resp = client.delete(url)
        assert resp.status_code == http.HTTPStatus.NOT_FOUND
