from sqlalchemy import func, and_

from src.models.my_models import Employee, Department


class EmployeeService:
    @staticmethod
    def fetch_all_employees(session):
        return session.query(Employee)

    @staticmethod
    def fetch_all_employees_by_dep(session, id):
        return session.query(Employee).filter(Employee.department_id == id)

    @staticmethod
    def fetch_all_employees_with_dep(session):
        return session.query(Employee.id, Employee.name, Employee.birthday, Employee.salary,
                             Employee.department_id, Department.name.label('dep')).join(Department)

    @staticmethod
    def fetch_all_employees_with_dep_between_dates(session, date1, date2):
        return session.query(Employee.id, Employee.name, Employee.birthday, Employee.salary,
                             Employee.department_id, Department.name.label('dep')). \
            join(Department).filter(and_(
            Employee.birthday > date1,
            Employee.birthday < date2
        ))

    @classmethod
    def fetch_employee_by_id(cls, session, id):
        return cls.fetch_all_employees(session).filter_by(id=id).first()


class DepartmentService:
    @staticmethod
    def fetch_all_departments(session):
        return session.query(Department)

    @staticmethod
    def fetch_all_departments_with_avg_salary(session):
        return session.query(Department.id, Department.name,
                             func.avg(Employee.salary).label('avg')).group_by(Department.id).join(Department)

    @classmethod
    def fetch_department_by_id(cls, session, id):
        return cls.fetch_all_departments(session).filter_by(id=id).first()

    @classmethod
    def fetch_department_by_name(cls, session, name):
        return cls.fetch_all_departments(session).filter_by(
            name=name
        ).first()
