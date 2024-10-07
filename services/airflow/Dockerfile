# ARG build_for=linux/amd64

# FROM --platform=${build_for} apache/airflow:2.10.2-python3.8
FROM apache/airflow:2.10.2-python3.8

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.2/constraints-3.8.txt"