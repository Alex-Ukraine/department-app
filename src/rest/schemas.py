from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.models.my_models import Employee, Department


class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True


class EmployeeSchemaWithDep(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True

    dep = fields.String(required=False)


class DepartmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True


class DepartmentSchema_Without_Id(SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True
        exclude = ['id']


class DepartmentSchemaWithAVG(SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True

    avg = fields.Float(required=True, default=0)
