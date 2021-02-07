#!/bin/python3
''' foreman exporter '''
import datetime
import distutils.core
import json
import os
import time
import urllib

import requests
from prometheus_client import Summary, start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Variables
FOREMAN_HOSTS_BODY = None
FOREMAN_HOSTS_RESPONSE = None

try:
    if os.getenv("FOREMAN_REQUEST_URI") is not None:
        REQUEST_URI = str(os.getenv("FOREMAN_REQUEST_URI")+'/api/hosts/')
        REQUEST_HOSTNAME = (urllib.parse.urlparse(REQUEST_URI)).netloc
    else:
        REQUEST_URI = "https://foreman.sample.com/api/hosts"
        REQUEST_HOSTNAME = (urllib.parse.urlparse(REQUEST_URI)).netloc
    if os.getenv("FOREMAN_REQUEST_USER") is not None:
        REQUEST_USER = str(os.getenv("FOREMAN_REQUEST_USER"))
    else:
        REQUEST_USER = "api"
    if os.getenv("FOREMAN_REQUEST_PASSWORD") is not None:
        REQUEST_PASSWORD = str(os.getenv("FOREMAN_REQUEST_PASSWORD"))
    else:
        REQUEST_PASSWORD = "api"
    if os.getenv("FOREMAN_REQUEST_TLS_VERIFY") is not None:
        REQUEST_TLS_VERIFY = distutils.util.strtobool((os.getenv("FOREMAN_REQUEST_TLS_VERIFY")))
    else:
        REQUEST_TLS_VERIFY = False
    if os.getenv("FOREMAN_REQUEST_TIMEOUT") is not None:
        REQUEST_TIMEOUT = int(os.getenv("FOREMAN_REQUEST_TIMEOUT"))
    else:
        REQUEST_TIMEOUT = 60
    if os.getenv("FOREMAN_REQUEST_INTERVAL") is not None:
        REQUEST_INTERVAL = int(os.getenv("FOREMAN_REQUEST_INTERVAL"))
    else:
        REQUEST_INTERVAL = 120
except NameError:
    timestamp = datetime.datetime.now()
    print(timestamp, "Evaluation of Environmental Variables failed, returning to defaults")

if all(v_check is not None for v_check in [REQUEST_URI, REQUEST_HOSTNAME, REQUEST_USER, REQUEST_PASSWORD, REQUEST_TLS_VERIFY, REQUEST_TIMEOUT, REQUEST_INTERVAL]):
    pass
else:
    timestamp = datetime.datetime.now()
    print(timestamp, "One of variables is empty")
    raise SystemExit(1)

print("Variables:")
print(f"REQUEST_URI        = {REQUEST_URI}")
print(f"REQUEST_HOSTNAME   = {REQUEST_HOSTNAME}")
print(f"REQUEST_USER       = {REQUEST_USER}")
# getpass to hide passwords?
print(f"REQUEST_PASSWORD   = {REQUEST_PASSWORD}")
print(f"REQUEST_TLS_VERIFY = {REQUEST_TLS_VERIFY}")
print(f"REQUEST_TIMEOUT    = {REQUEST_TIMEOUT}")
print(f"REQUEST_INTERVAL   = {REQUEST_INTERVAL}")


# initial data
def f_requests_hosts():
    ''' Process Foreman's hosts response '''
    global FOREMAN_HOSTS_RESPONSE
    global FOREMAN_HOSTS_BODY
    try:
        response = requests.get(REQUEST_URI, auth=(REQUEST_USER, REQUEST_PASSWORD), verify=REQUEST_TLS_VERIFY, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        body = json.loads(response.text)
        if 200 >= response.status_code <= 399:
            l_timestamp = datetime.datetime.now()
            print(l_timestamp, "Request at", REQUEST_URI, "with code", response.status_code, "took", response.elapsed.seconds, "seconds")
            FOREMAN_HOSTS_BODY = body
            FOREMAN_HOSTS_RESPONSE = response
        else:
            l_timestamp = datetime.datetime.now()
            print(l_timestamp, "Response code not proper", response.status_code)
    except requests.exceptions.RequestException as err:
        l_timestamp = datetime.datetime.now()
        print(l_timestamp, "Request at", REQUEST_URI, "failed with code", err)
        time.sleep(1)
        raise SystemExit(err) from err


# register class
class RequestsHosts:
    ''' Register Prometheus Metrics for Foremant's hosts '''
    def __init__(self):
        pass

    @staticmethod
    def collect():
        ''' foremans gauges '''
        g_hosts = GaugeMetricFamily("foreman_exporter_hosts", 'foreman host status', labels=['hostname', 'domain', 'configuration', 'configuration_label',
                                    'puppet_status', 'global_label', 'environment', 'operatingsystem', 'foreman_hostname'])
        if FOREMAN_HOSTS_BODY is not None:
            for each in FOREMAN_HOSTS_BODY['results']:
                name = str(each['name'])
                domain = str(each['domain_name'])
                status = (each['global_status'])
                global_label = str(each['global_status_label'])
                configuration_status = str(each['configuration_status'])
                configuration_status_label = str(each['configuration_status_label'])
                puppet_status = str(each['puppet_status'])
                environment_name = str(each['environment_name'])
                operatingsystem = str(each['operatingsystem_name'])
                if (
                  name is None or domain is None or status is None or configuration_status is None or configuration_status_label is None
                  ):
                    continue
                if global_label is None:
                    global_label = '199'
                if puppet_status is None:
                    puppet_status = '199'
                if environment_name is None:
                    environment_name = 'unknown'
                if operatingsystem is None:
                    operatingsystem = 'unknown'
                g_hosts.add_metric([name, domain, configuration_status, configuration_status_label, puppet_status, global_label,
                                    environment_name, operatingsystem, REQUEST_HOSTNAME], status)
            yield g_hosts
        else:
            pass
        # How long the process was made
        if FOREMAN_HOSTS_RESPONSE.elapsed.seconds is not None:
            g_hosts_time = GaugeMetricFamily("foreman_exporter_hosts_request_time_seconds", 'foreman host request time seconds', labels=['foreman_hostname'])
            g_hosts_time.add_metric([REQUEST_HOSTNAME], int(FOREMAN_HOSTS_RESPONSE.elapsed.seconds))
            yield g_hosts_time
        else:
            pass
        # number of hosts
        if FOREMAN_HOSTS_BODY is not None:
            g_hosts_count = GaugeMetricFamily("foreman_exporter_hosts_count", 'foreman host count', labels=['foreman_hostname'])
            g_hosts_count.add_metric([REQUEST_HOSTNAME], int(FOREMAN_HOSTS_BODY['total']))
            yield g_hosts_count
        else:
            pass


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


@REQUEST_TIME.time()
def f_process_request():
    """A dummy function that takes some time."""
    time.sleep(REQUEST_INTERVAL)


def f_start_http():
    ''' Start http server '''
    l_timestamp = datetime.datetime.now()
    print(l_timestamp, "Starting http server")
    # Start up the server to expose the metrics.
    start_http_server(8000)


if __name__ == '__main__':
    # Initial fill in
    f_requests_hosts()
    f_start_http()
    # Register gauges
    REGISTRY.register(RequestsHosts())
    # Generate some requests.
    while True:
        f_process_request()
        f_requests_hosts()
