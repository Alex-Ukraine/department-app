import json

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from src import db, api
from src.rest.schemas import EmployeeSchema, DepartmentSchema, DepartmentSchema_Without_Id, DepartmentSchemaWithAVG, EmployeeSchemaWithDep
from src.service.service import EmployeeService, DepartmentService


class EmployeeListApi(Resource):
    employee_schema = EmployeeSchema()
    employee_schema_with_dep = EmployeeSchemaWithDep()
    department_schema_without_id = DepartmentSchema_Without_Id()

    def get(self, id=None):
        if not id:
            rq = request.args
            if rq:
                date1 = rq.get('date1')
                date2 = rq.get('date2')
                employees = EmployeeService.fetch_all_employees_with_dep_between_dates(db.session, date1=date1, date2=date2).all()
            else:
                employees = EmployeeService.fetch_all_employees_with_dep(db.session).all()
            return self.employee_schema_with_dep.dump(employees, many=True), 200

        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return '', 404
        return self.employee_schema(employee), 200

    def post(self):
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
            employee = self.employee_schema.load(rq, session=db.session)
        except ValidationError as e:
            return {'message': str(e)}, 400

        db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 201

    def put(self, id):
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return "", 404
        try:
            employee = self.employee_schema.load(request.json, instance=employee, session=db.session)
        except ValidationError as e:
            return {'message': str(e)}, 400
        db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 200

    def patch(self, id):
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
            return {'Message': f'error: {e}'}, 400
        db.session.add(employee)
        db.session.commit()
        return self.employee_schema.dump(employee), 200

    def delete(self, id):
        employee = EmployeeService.fetch_employee_by_id(db.session, id)
        if not employee:
            return '', 404
        db.session.delete(employee)
        db.session.commit()
        return '', 204


class DepartmentListApi(Resource):
    department_schema = DepartmentSchema()
    department_schema_with_avg = DepartmentSchemaWithAVG()

    def get(self, id=None):
        if not id:
            departments = DepartmentService.fetch_all_departments_with_avg_salary(db.session).all()
            departments_with_none_salary = DepartmentService.fetch_all_departments(db.session).all()
            return self.department_schema_with_avg.dump(departments, many=True), 200

        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return '', 404
        return self.department_schema(department), 200

    def post(self):
        try:
            department = self.department_schema.load(request.json, session=db.session)
        except ValidationError as e:
            return {'message': str(e)}, 400
        db.session.add(department)
        db.session.commit()
        return self.department_schema.dump(department), 201

    def put(self, id):
        department = EmployeeService.fetch_department_by_id(db.session, id)
        if not department:
            return "", 404
        try:
            department = self.department_schema.load(request.json, instance=department, session=db.session)
        except ValidationError as e:
            return {'message': str(e)}, 400
        db.session.add(department)
        db.session.commit()
        return self.department_schema.dump(department), 200

    def patch(self, id):
        department = DepartmentService.fetch_department_by_id(db.session, id)
        if not department:
            return '', 404
        try:
            department = self.department_schema.load(request.json, instance=department, session=db.session,
                                                     partial=True)
        except ValidationError as e:
            return {'Message': f'error: {e}'}, 400
        db.session.add(department)
        db.session.commit()
        return self.department_schema.dump(department), 200

    def delete(self, id):
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
        return '', 200


api.add_resource(EmployeeListApi, '/json/employees', '/json/employees/<id>', strict_slashes=False)
api.add_resource(DepartmentListApi, '/json/departments', '/json/departments/<id>', strict_slashes=False)
