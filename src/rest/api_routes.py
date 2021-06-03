import copy

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import ValidationError
from sqlalchemy import text

from src import db, api, app, logger
from src.rest.schemas import EmployeeSchema, DepartmentSchema
from src.service.service import EmployeeService, DepartmentService


@app.before_request
def before_request():
    try:
        db.engine.execute(text("SELECT 1"))
    except Exception as e:
        return make_response(jsonify({"message": f"No connection with DB(generally): {e}"}), 500)


class EmployeeListApi(Resource):
    employee_schema = EmployeeSchema(only=("id", "name", "birthday", "salary", "department_id"))
    employee_schema_with_dep = EmployeeSchema()
    department_schema_without_id = DepartmentSchema(only=("name",))

    def get(self, id=None):
        """send get request with data(id, date1, date2) or not and return json data, and if answer to request
        to db not empty json will have fields 'dep', 'department_id','name', 'salary', 'id','birthday'"""
        if not id:
            rq = request.args
            if rq.get('date1') and rq.get('date2'):
                date1 = rq.get('date1')
                date2 = rq.get('date2')
                employees = EmployeeService.fetch_all_employees_with_dep_between_dates(db.session, date1=date1,
                                                                                       date2=date2).all()
            elif rq.get('department_id'):
                employees = EmployeeService.fetch_all_employees_by_dep_with_names_dep(db.session,
                                                                                      id=rq.get('department_id')).all()
            else:
                employees = EmployeeService.fetch_all_employees_with_dep(db.session).all()
            return self.employee_schema_with_dep.dump(employees, many=True), 200

        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        logger.debug(employee)
        if not employee:
            return make_response(jsonify({"message": "Employee not found"}), 404)
        return self.employee_schema.dump(employee), 200

    def post(self):
        """send post request to db with json(fields: 'dep','name', 'salary', 'birthday') and return
        json data(fields: 'dep', 'department_id','name', 'salary', 'id','birthday'.
        If department not exist algorithm creates new department in db"""
        rq_args = request.args
        rq = request.json
        if not rq_args.get('populate'):
            rq = [rq]
        logger.debug(rq)
        for one_record in rq:
            department_name = one_record['department_name']
            department = DepartmentService.fetch_department_by_name(db.session, name=department_name)

            if not department:
                department = self.department_schema_without_id.load(dict(name=department_name), session=db.session)
                DepartmentService.create(department, db.session)

            dep_record = copy.deepcopy(one_record)
            dep_record['department_id'] = department.id
            del dep_record['department_name']
            try:
                employee = self.employee_schema.load(dep_record, session=db.session)
            except ValidationError as e:
                logger.debug(f"Validation error to post Employee {one_record} by Api is {e}")
                return make_response(jsonify({'message': f'Validation error to post Employee {one_record} is {e}'}),
                                     400)
            db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 201

    def put(self, id):
        """send put request with json(fields: 'department_id','name', 'salary', 'birthday') and return
        json data(fields: 'dep', 'department_id','name', 'salary', 'id','birthday'.
        If department not exist algorithm creates new department in db.
        Every field must be filled"""
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return make_response(jsonify({"message": "Employee not found"}), 404)
        rq = request.json
        department_name = rq['department_name']
        department = DepartmentService.fetch_department_by_name(db.session, name=department_name)
        if not department:
            department = self.department_schema_without_id.load(dict(name=department_name), session=db.session)
            DepartmentService.create(department, db.session)
        rq['department_id'] = department.id
        del rq['department_name']
        try:
            employee = self.employee_schema.load(request.json, instance=employee, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in put Employee by Api is {e}")
            return make_response(jsonify({'message': str(e)}), 400)
        return self.employee_schema.dump(EmployeeService.create(employee, db.session)), 200

    def patch(self, id):
        """send patch request with json(fields: 'department_id','name', 'salary', 'birthday') and return
                json data(fields: 'dep', 'department_id','name', 'salary', 'id','birthday'.
                If department not exist algorithm creates new department in db."""
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return make_response(jsonify({"message": "Employee not found"}), 404)
        rq = request.json
        department_name = rq['department_name']
        department = DepartmentService.fetch_department_by_name(db.session, name=department_name)
        if not department:
            department = self.department_schema_without_id.load(dict(name=department_name), session=db.session)
            DepartmentService.create(department, db.session)
        rq['department_id'] = department.id
        del rq['department_name']
        try:
            employee = self.employee_schema.load(rq, instance=employee, session=db.session,
                                                 partial=True)
        except ValidationError as e:
            logger.debug(f"Validation error in patch Employee by Api is {e}")
            return make_response(jsonify({'Message': f'error: {e}'}), 400)
        return self.employee_schema.dump(EmployeeService.create(employee, db.session)), 200

    def delete(self, id):
        """send delete request to db(table 'employee') with json(fields: 'department_id','name',
        'salary', 'birthday') and return status code 204 or 404"""
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return make_response(jsonify({"message": "Employee not found"}), 404)
        EmployeeService.delete(employee, db.session)
        return '', 204


class DepartmentListApi(Resource):
    department_schema = DepartmentSchema(only=("id", "name", "employees"))
    department_schema_with_avg = DepartmentSchema(only=("id", "name", "avg", "count"))

    def get(self, id=None):
        """send get request with id or no to db(joined query between tables employee and department)
        and return json data, and if answer to request to db not empty json will have fields 'department_id',
        'name', 'avg'. It is not json with list of all departments, only departments which binded with employees"""
        if not id:
            field = request.args.get('field', 'id')
            ordr = request.args.get('ordr', 'asc')
            departments = DepartmentService.fetch_all_departments_with_avg_salary_sort_by(db.session, field, ordr).all()
            return self.department_schema_with_avg.dump(departments, many=True), 200

        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return make_response(jsonify({"message": "Department not found"}), 404)
        return self.department_schema.dump(department), 200

    def post(self):
        """send post request to db(joined query between tables employee and department) json(fields: 'dep')
        and return json data(fields: 'id','name'). If department not exist algorithm creates new department in db"""
        try:
            department = self.department_schema.load(request.json, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in post Department by Api is {e}")
            return make_response(jsonify({'message': str(e)}), 400)
        if DepartmentService.fetch_department_by_name(db.session, department.name):
            logger.debug('Department not unique, already exists')
            return make_response(jsonify({'message': 'Department not unique, already exists'}), 409)
        return self.department_schema.dump(DepartmentService.create(department, db.session)), 201

    def put(self, id):
        """send put request with json(fields: 'id','name') and return json data(fields: 'name', 'id')."""
        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return make_response(jsonify({"message": "Department not found"}), 404)

        employees = EmployeeService.update_department_id(db.session, id=id,
                                                         name=request.json['name'])
        logger.debug(employees)

        dep_by_name = DepartmentService.fetch_department_by_name(db.session, name=request.json['name'])

        if dep_by_name:
            return self.department_schema.dump(DepartmentService.delete(department, db.session)), 200

        try:
            department = self.department_schema.load(request.json, instance=department, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in put Department by Api is {e}")
            return make_response(jsonify({'message': str(e)}), 400)
        logger.debug(department)
        return self.department_schema.dump(DepartmentService.create(department, db.session)), 200

    def delete(self, id):
        """send delete request to db(table 'department') with json(fields: 'id','name')
        and return status code 204 or 404"""

        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return make_response(jsonify({"message": "Department not found"}), 404)
        DepartmentService.delete(department, db.session)
        return '', 204


api.add_resource(EmployeeListApi, '/json/employees', '/json/employees/<id>', strict_slashes=False)
api.add_resource(DepartmentListApi, '/json/departments', '/json/departments/<id>', strict_slashes=False)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL,
                                               config={'app_name': "department-app flask restful api"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
