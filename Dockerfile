FROM python:3.8

RUN useradd --create-home wincity18
WORKDIR /department-app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .. .

RUN chown -R wincity18:wincity18 ./
USER wincity18

EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app