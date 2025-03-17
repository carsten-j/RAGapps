FROM python:3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app.py /code/app/app.py

CMD ["fastapi", "run", "app/app.py", "--port", "5000"]