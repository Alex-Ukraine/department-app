from src.models.my_models import Employee


class EmployeeService:
    @staticmethod
    def fetch_all_employees(session):
        return session.query(Employee)