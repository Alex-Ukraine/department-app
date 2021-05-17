from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.models.my_models import Employee


class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        exclude = ['id']
        load_instance = True
        include_fk = True
