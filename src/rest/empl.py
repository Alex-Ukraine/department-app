from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.orm import selectinload

from src import db, api, app, logger
from src.models.my_models import Department
from src.rest.schemas import EmployeeSchema, DepartmentSchema
from src.service.service import EmployeeService, DepartmentService


class EmployeeListApi(Resource):
    employee_schema = EmployeeSchema(only=("id", "name", "birthday", "salary", "department_id",))
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
        if not employee:
            return '', 404
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
        for one in rq:
            dep = one['dep']
            department = DepartmentService.fetch_department_by_name(db.session, name=dep)

            if not department:
                department = self.department_schema_without_id.load(dict(name=dep), session=db.session)
                db.session.add(department)
                db.session.commit()

            one['department_id'] = department.id
            del one['dep']
            try:
                employee = self.employee_schema.load(one, session=db.session)
            except ValidationError as e:
                logger.debug(f"Validation error to post Employee by Api is {e}")
                return {'message': f'Validation error to post Employee {e}'}, 400
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
            return "", 404
        rq = request.json
        dep = rq['dep']
        department = DepartmentService.fetch_department_by_name(db.session, name=dep)
        if not department:
            department = self.department_schema_without_id.load(dict(name=dep), session=db.session)
            db.session.add(department)
            db.session.commit()
        rq['department_id'] = department.id
        del rq['dep']
        try:
            employee = self.employee_schema.load(request.json, instance=employee, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in put Employee by Api is {e}")
            return {'message': str(e)}, 400
        db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 200

    def patch(self, id):
        """send patch request with json(fields: 'department_id','name', 'salary', 'birthday') and return
                json data(fields: 'dep', 'department_id','name', 'salary', 'id','birthday'.
                If department not exist algorithm creates new department in db."""
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return '', 404
        rq = request.json
        dep = rq['dep']
        department = DepartmentService.fetch_department_by_name(db.session, name=dep)
        if not department:
            department = self.department_schema_without_id.load(dict(name=dep), session=db.session)
            db.session.add(department)
            db.session.commit()
        rq['department_id'] = department.id
        del rq['dep']
        try:
            employee = self.employee_schema.load(rq, instance=employee, session=db.session,
                                                 partial=True)
        except ValidationError as e:
            logger.debug(f"Validation error in patch Employee by Api is {e}")
            return {'Message': f'error: {e}'}, 400
        db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 200

    def delete(self, id):
        """send delete request to db(table 'employee') with json(fields: 'department_id','name',
        'salary', 'birthday') and return status code 204 or 404"""
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return {"message": "BAD REQUEST"}, 404
        db.session.delete(employee)
        db.session.commit()
        return '', 204


class DepartmentListApi(Resource):
    department_schema = DepartmentSchema(only=("id", "name"))
    department_schema_with_avg = DepartmentSchema(only=("id", "name", "avg", "count"))
    """department_schema = DepartmentSchema()
    department_schema_with_avg = DepartmentSchemaWithAVG()"""

    def get(self, id=None):
        """send get request with id or no to db(joined query between tables employee and department)
        and return json data, and if answer to request to db not empty json will have fields 'department_id',
        'name', 'avg'. It is not json with list of all departments, only departments which binded with employees"""
        if not id:
            departments = DepartmentService.fetch_all_departments_with_avg_salary(db.session).all()
            return self.department_schema_with_avg.dump(departments, many=True), 200

        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return '', 404
        return self.department_schema_with_avg.dump(department), 200

    def post(self):
        """send post request to db(joined query between tables employee and department) json(fields: 'dep')
        and return json data(fields: 'id','name'). If department not exist algorithm creates new department in db"""
        try:
            department = self.department_schema.load(request.json, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in post Department by Api is {e}")
            return {'message': str(e)}, 400
        if DepartmentService.fetch_department_by_name(db.session, department.name):
            logger.debug('Department not unique, already exists')
            return {'message': 'Department not unique, already exists'}, 409
        db.session.add(department)
        db.session.commit()

        return self.department_schema.dump(department), 201

    def put(self, id):
        """send put request with json(fields: 'id','name') and return json data(fields: 'name', 'id')."""
        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return "", 404

        # update employees department_id into new department_id and delete updated department
        department2 = DepartmentService.fetch_department_by_name(db.session, request.json['name'])
        if department2:
            employees = EmployeeService.fetch_all_employees_by_dep(db.session, id).all()
            if employees:
                for x in employees:
                    x.department_id = department2.id
                    logger.debug(x)
                    db.session.add(x)
            db.session.delete(department)
            db.session.commit()
            return self.department_schema.dump(department2), 200
        try:
            department = self.department_schema.load(request.json, instance=department, session=db.session)
        except ValidationError as e:
            logger.debug(f"Validation error in put Department by Api is {e}")
            return {'message': str(e)}, 400
        db.session.add(department)
        db.session.commit()
        return self.department_schema.dump(department), 200

    def delete(self, id):
        """send delete request to db(table 'department') with json(fields: 'id','name')
        and return status code 204 or 404"""
        employees = EmployeeService.fetch_all_employees_by_dep(db.session, id).all()
        if employees:
            for x in employees:
                db.session.delete(x)
            db.session.commit()

        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return '', 404
        db.session.delete(department)
        db.session.commit()
        return '', 204


api.add_resource(EmployeeListApi, '/json/employees', '/json/employees/<id>', strict_slashes=False)
api.add_resource(DepartmentListApi, '/json/departments', '/json/departments/<id>', strict_slashes=False)
