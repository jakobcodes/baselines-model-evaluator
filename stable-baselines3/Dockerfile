FROM python:3.9

ENV USERNAME=oracle-stable-baselines3
ENV WORKING_DIR=/home/oracle-stable-baselines3

WORKDIR ${WORKING_DIR}

COPY app app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV FLASK_APP=app

EXPOSE 8080

CMD ["python", "app/api.py"]