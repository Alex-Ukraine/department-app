from datetime import datetime

from marshmallow import fields, validates, ValidationError, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.models.my_models import Employee, Department


class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True

    name = fields.Str(validate=validate.Regexp(r'^[A-Za-zА-Яа-я\s\'`\.]{1,100}$'))
    department_name = fields.String(required=True, dump_only=True)

    @validates("birthday")
    def validate_birthday(self, value):
        if value < datetime.strptime('1930-01-01', '%Y-%m-%d').date():
            raise ValidationError("birthday must be greater than 1930.")
        if value > datetime.strptime('2015-01-01', '%Y-%m-%d').date():
            raise ValidationError("birthday must not be greater than 2015.")


class DepartmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True

    employees = fields.Nested("EmployeeSchema", many=True, only=["id", "name", "birthday", "salary", "department_id"])
    avg = fields.Float(required=True, default=0, dump_only=True)
    count = fields.Float(required=True, default=0, dump_only=True)
