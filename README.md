## department-app

>department-app (“Employees”) is web-application with webservices which allows users to record, change, populate, search, delete and generate some statistical information about employees and departments.
Application should provide:
- Storing tables employees and departments with data in a database;
- Departments should store their names;
- Employees should store the following data: related department, employee name, date of
birth, salary;
- Display list employees;
- Updating the list of employees (adding, editing, removing);
- Display list of departments;
- Updating the list of departments (adding, editing, removing);
- Populate database with the test data;
- Web service(RESTful) for CRUD operations returns data stored in the database;
- Web application uses web service to fetch the data from database;
- Display a list of departments and the average salary (calculated automatically) for these
departments;
- Display a list of employees in the departments with an indication of the salary for each
employee and a search field to search for employees born on a certain date or in the
period between dates;

Web version of a part of this project available on Heroku [alex-app-flask.herokuapp.com](https://alex-app-flask.herokuapp.com/)
>> Web application will be available after launch on address(uri) '/'
> 
>> Web services will be available after launch on address(uri) '/json'
 
If you want test this project on your local machine run the following commands:

> git init
> git clone https://github.com/Alex-Ukraine/department-app.git
> 
Then create virtual environment:

> virtualenv venv

Activate this environment:

>On Linux/Mac
>> venv/bin/activate
>>
>On Windows
>> venv/Scripts/activate

Install all dependencies:
> for ubuntu: sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
> pip install -r requirements.txt
> 
> sudo apt update
> sudo apt install mysql-server
> sudo mysql
> ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '';
> CREATE DATABASE finalproject

Then you need set your app to Flask with command:

>On Linux/Mac
>> set FLASK_APP=wsgi.py
>>
>On Windows
>> set FLASK_APP=wsgi.py

Then run migrations:

> flask db upgrade

And now you can start this app:

> flask run
