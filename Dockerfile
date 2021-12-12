FROM python:3.10.1-alpine AS stage
COPY app/* /app/
RUN apk add --no-cache --update -t deps curl tzdata \
  && python -m pip install --upgrade pip --no-cache-dir \
  && pip install --no-cache-dir -r /app/pip-requirements.txt \
  && addgroup -S python-group && adduser -G python-group -S python-user \
  && rm -rfv /tmp
USER python-user
WORKDIR /app
ENV PYTHONPATH '/app/'
ENV TZ "Europe/Warsaw"
LABEL version="0.0.12"
LABEL release="foreman_exporter"
LABEL maintainer="marcinbojko"
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000 || exit 1
EXPOSE 8000
CMD ["python","-u","/app/foreman_exporter.py"]
