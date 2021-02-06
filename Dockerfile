FROM python:3.9.1-alpine
COPY app/* /app/
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r /app/pip-requirements.txt
WORKDIR /app
ENV PYTHONPATH '/app/'
LABEL VERSION="0.0.1"
LABEL RELEASE="foreman_exporter"
EXPOSE 8000
CMD ["python" , "/app/foreman_exporter.py"]
