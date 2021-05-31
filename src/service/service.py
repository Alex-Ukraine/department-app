from sqlalchemy import func, and_

from src.models.my_models import Employee, Department


class EmployeeService:
    @staticmethod
    def fetch_all_employees(session):
        """make a query to db table 'employee' and fetch all records"""
        return session.query(Employee)

    """@staticmethod
    def fetch_all_employees_by_dep(session, id):
        return session.query(Employee).filter(Employee.department_id == id)"""

    @staticmethod
    def fetch_all_employees_by_dep_with_names_dep(session, id):
        """make a query to db table 'employee' and fetch records who satisfies condition
        'Employee.department_id == id'"""
        return session.query(Employee.id, Employee.name, Employee.birthday, Employee.salary,
                             Employee.department_id, Department.name.label('department_name')).join(Department).filter(
            Employee.department_id == id)

    @staticmethod
    def fetch_all_employees_with_dep(session):
        """make a query to db table 'employee' and 'department', fetch all records + add new field 'dep',
         filled with values from table 'department'"""
        return session.query(Employee.id, Employee.name, Employee.birthday, Employee.salary,
                             Employee.department_id, Department.name.label('department_name')).join(Department)

    @staticmethod
    def fetch_all_employees_with_dep_between_dates(session, date1, date2):
        """make a query to db(table 'employee' and 'department') with parameters date1 and date2, fetch all records,
         who satisfies condition 'Employee.birthday > date1, Employee.birthday < date2'
         + add new field 'dep', filled with values from table 'department'.

         SELECT Employee.id, Employee.name, Employee.birthday, Employee.salary, Employee.department_id,
         Department.name AS 'dep' FROM employee LEFT JOIN department on
         employee.department_id = department.id WHERE Employee.birthday BETWEEN '1985-01-01' AND '1991-01-01';"""
        return session.query(Employee.id, Employee.name, Employee.birthday, Employee.salary,
                             Employee.department_id, Department.name.label('department_name')). \
            join(Department).filter(and_(
            Employee.birthday > date1,
            Employee.birthday < date2
        ))

    @classmethod
    def fetch_employee_by_id(cls, session, id):
        """make a query to db table 'employee' and fetch records who satisfies condition
                'Employee.id == id'"""
        return cls.fetch_all_employees(session).filter_by(id=id).first()

    @classmethod
    def update_department_id(cls, session, id, name):
        department_id = DepartmentService.fetch_department_by_name(session=session, name=name)
        if department_id:
            department_id = department_id.id
        return session.query(Employee).filter(Employee.department_id == id).update(
            {Employee.department_id: department_id})

    @classmethod
    def create(cls, self, session):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def delete(cls, self, session):
        session.delete(self)
        session.commit()


class DepartmentService:
    @classmethod
    def create(cls, self, session):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def delete(cls, self, session):
        session.delete(self)
        session.commit()

    @staticmethod
    def fetch_all_departments(session):
        """make a query to db table 'department' and fetch all records"""
        return session.query(Department)

    @staticmethod
    def fetch_all_departments_with_avg_salary(session):
        """SELECT department.name, AVG(employee.salary), COUNT(employee.id) FROM employee
        RIGHT JOIN department on employee.department_id = department.id
        GROUP BY department.id;"""
        return session.query(Department.id, Department.name,
                             func.coalesce(func.avg(Employee.salary), 0).label('avg'),
                             func.count(Employee.id).label('count')).group_by(Department.id).join(Employee,
                                                                                                  isouter=True)

    @classmethod
    def fetch_department_by_id(cls, session, id):
        return cls.fetch_all_departments(session).filter_by(id=id).first()

    @classmethod
    def fetch_department_by_name(cls, session, name):
        return cls.fetch_all_departments(session).filter_by(
            name=name
        ).first()
