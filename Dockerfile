FROM python:3.6-slim
WORKDIR /app
RUN ["/bin/bash", "-c", "mkdir /app/logs"]
COPY requirements.txt /app/
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY ./tweetl /app/tweetl/
COPY setup.py /app/
RUN pip install /app
COPY .env /app/
RUN ["/bin/bash", "-c", "source /app/.env"]
ENTRYPOINT ["python", "tweetl"]
