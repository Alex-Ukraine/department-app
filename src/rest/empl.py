from flask_restful import Resource

from src import db
from src.rest.schemas import EmployeeSchema
from src.service.service import EmployeeService


class EmployeeListApi(Resource):
    employee_schema = EmployeeSchema()

    def get(self):
        employees = EmployeeService.fetch_all_employees(db.session).all()
        return self.employee_schema.dump(employees, many=True), 200

"""    def post(self):
        try:
            film = self.film_schema.load(request.json, session=db.session)
        except ValidationError as e:
            return {'message': str(e)}, 400
        db.session.add(film)
        db.session.commit()
        return self.film_schema.dump(film), 201"""