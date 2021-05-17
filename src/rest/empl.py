from flask_restful import Resource

from src import db

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.models.my_models import Employee


class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        exclude = ['id']
        load_instance = True
        include_fk = True


class EmployeeService:
    @staticmethod
    def fetch_all_employees(session):
        return session.query(Employee)


class EmployeeListApi(Resource):
    employee_schema = EmployeeSchema()

    def get(self):
        employees = EmployeeService.fetch_all_employees(db.session).all()
        return self.employee_schema.dump(employees, many=True), 200
