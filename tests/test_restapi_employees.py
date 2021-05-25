import http
import json
from dataclasses import dataclass
from unittest.mock import patch

from src import app, db
from src.models.my_models import Department


@dataclass
class FakeEmployee:
    name = 'Fake Employee'
    birthday = '1990-03-05'
    salary = 150
    department_id = 1


class TestRestEmployees:
    id = []

    def test_populate_db(self):
        client = app.test_client()
        client.get('/populate/20')

    def test_get_employees_with_db(self):
        client = app.test_client()
        resp = client.get('/json/employees')

        assert resp.status_code == http.HTTPStatus.OK

    def test_get_employee_by_id_with_db_get_404(self):
        client = app.test_client()
        resp = client.get('/json/employees/99999999999999')

        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_get_employees_with_db_between_dates(self):
        client = app.test_client()
        resp = client.get('/json/employees/?date1=1985-07-22&date2=2000-07-22')
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_employees_with_db_selected_with_department_id(self):
        client = app.test_client()
        resp = client.get('/json/employees/?department_id=1')
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_employees_mock_db(self):
        with patch('src.service.service.EmployeeService.fetch_all_employees_with_dep', autospec=True) as mock_db_call:
            client = app.test_client()
            resp = client.get('/json/employees')

            mock_db_call.assert_called_once()
            assert resp.status_code == http.HTTPStatus.OK
            assert len(resp.json) == 0

    def test_create_employee_with_db(self):
        client = app.test_client()
        data = {
            "name": "Fake Employee",
            "birthday": "1990-03-05",
            "salary": 1000,
            "dep": "frontend"
        }
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.CREATED
        assert resp.json['name'] == 'Fake Employee'
        self.id.append(resp.json['id'])

    def test_create_employee_with_db_no_dep(self):
        client = app.test_client()
        data = {
            "name": "Fake Employee",
            "birthday": "1990-03-05",
            "salary": 1000,
            "dep": 'some super mega strange name department'
        }
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.CREATED
        assert resp.json['name'] == 'Fake Employee'
        self.id.append(resp.json['id'])

    def test_create_employee_with_db_error_validation_400(self):
        client = app.test_client()
        data = {
            "name": "Fake Employee",
            "birthday": "1990-03-05",
            "salary": 1000,
            "dep": "web",
            "mood": "crazy"
        }
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_create_employee_with_db_error_validation_400_incompatible_date1(self):
        client = app.test_client()
        data = {
            "name": "Fake Employee",
            "birthday": "2020-03-05",
            "salary": 1000,
            "dep": "web"
        }
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_create_employee_with_db_error_validation_400_incompatible_date2(self):
        client = app.test_client()
        data = {
            "name": "Fake Employee",
            "birthday": "1900-03-05",
            "salary": 1000,
            "dep": "web"
        }
        resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_get_employee_by_id_with_db(self):
        client = app.test_client()
        resp = client.get(f'/json/employees/{self.id[0]}')

        assert resp.status_code == http.HTTPStatus.OK

    def test_create_employee_with_mock_db(self):
        with patch('src.db.session.add', autospec=True) as mock_session_add, \
                patch('src.db.session.commit', autospec=True) as mock_session_commit:
            client = app.test_client()
            data = {
                "name": "Test Employee",
                "birthday": "1990-03-05",
                "salary": 560,
                "dep": "web"
            }
            resp = client.post('/json/employees', data=json.dumps(data), content_type='application/json')
            mock_session_add.assert_called_once()
            mock_session_commit.assert_called_once()

    def test_update_employee_with_db(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android"
        }
        resp = client.patch(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK
        assert resp.json['name'] == 'Update Name'

    def test_put_employee_with_db_not_found_404(self):
        client = app.test_client()
        url = f'/json/employees/888888888888'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_update_employee_with_db_not_found_404(self):
        client = app.test_client()
        url = f'/json/employees/888888888888'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android"
        }
        resp = client.patch(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_put_employee_with_db(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK
        assert resp.json['name'] == 'Update Name'

    def test_put_employee_with_db_error_validation_400(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android",
            "mood": "sad"
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_update_employee_with_db_error_validation_400(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": "android",
            "mood": "sad"
        }
        resp = client.patch(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.BAD_REQUEST

    def test_put_employee_with_db_new_dep(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-02",
            "dep": 'some department with freaky name'
        }
        resp = client.put(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK
        assert resp.json['name'] == 'Update Name'

    def test_update_employee_with_db_new_dep(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        data = {
            "name": "Update Name",
            "salary": 780,
            "birthday": "2010-04-01",
            "dep": 'some awesome new department'
        }
        resp = client.patch(url, data=json.dumps(data), content_type='application/json')
        assert resp.status_code == http.HTTPStatus.OK
        assert resp.json['name'] == 'Update Name'

    def test_update_employee_with_mock_db(self):
        with patch('src.service.service.EmployeeService.fetch_employee_by_id') as mocked_query, \
                patch('src.db.session.add', autospec=True) as mock_session_add, \
                patch('src.db.session.commit', autospec=True) as mock_session_commit, \
                patch('src.service.service.DepartmentService.fetch_department_by_name') as mocked_query2:
            mocked_query.return_value = FakeEmployee()
            client = app.test_client()
            url = f'/json/employees/{self.id[0]}'
            data = {
                "name": "Update Name",
                "salary": 150,
                "birthday": "2010-04-01",
                "dep": "android"
            }
            resp = client.patch(url, data=json.dumps(data), content_type='application/json')
            mocked_query2.assert_called_once()
            mock_session_add.assert_called_once()
            mock_session_commit.assert_called_once()

    def test_delete_employee_with_db(self):
        client = app.test_client()
        url = f'/json/employees/{self.id[0]}'
        resp = client.delete(url)
        assert resp.status_code == http.HTTPStatus.NO_CONTENT

    def test_delete_employee_with_db_no_such_id_404(self):
        client = app.test_client()
        url = f'/json/employees/666666666666'
        resp = client.delete(url)
        assert resp.status_code == http.HTTPStatus.NOT_FOUND

    def test_delete_department_with_db_if_employees_relate_exists(self):
        """It relates to test_restapi_departments module tests.
        But needs data from test_restapi_employees module tests"""
        temp_id_dep = db.session.query(Department).filter(Department.name == 'frontend').first().id
        client = app.test_client()
        url = f'/json/departments/{temp_id_dep}'
        resp = client.delete(url)
        assert resp.status_code == http.HTTPStatus.NO_CONTENT
