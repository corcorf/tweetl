FROM puckel/docker-airflow:1.10.9
USER root
RUN ["/bin/bash", "-c", "mkdir /app"]
RUN ["/bin/bash", "-c", "mkdir /app/logs"]
COPY requirements.txt /app/
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
COPY ./tweetl /app/tweetl/
COPY setup.py /app/
RUN pip install /app
COPY ./dags /usr/local/airflow/dags
COPY .env /
RUN ["/bin/bash", "-c", "source /.env"]
ENTRYPOINT ["python", "/app/tweetl"]
