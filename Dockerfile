FROM python:3.9.1-alpine
COPY app/* /app/
RUN apk add --no-cache --update -t deps curl \
  && python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/pip-requirements.txt
WORKDIR /app
ENV PYTHONPATH '/app/'
LABEL VERSION="0.0.2"
LABEL RELEASE="foreman_exporter"
LABEL MAINTAINER="marcinbojko"
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD curl --fail http://localhost:8000 || exit 1
EXPOSE 8000
CMD ["python","/app/foreman_exporter.py"]
