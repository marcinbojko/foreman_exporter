#!/bin/python3
''' foreman exporter '''
import datetime
import json
import distutils.core
import logging
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from json.decoder import JSONDecodeError

import httpx
from packaging import version
from prometheus_client import Summary, start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

# Variables
FOREMAN_HOSTS_BODY = None
FOREMAN_HOSTS_RESPONSE = None
FOREMAN_DASHBOARD_BODY = None
FOREMAN_DASHBOARD_RESPONSE = None
FOREMAN_STATUS_RESPONSE = None
FOREMAN_STATUS_BODY = None
FOREMAN_DASHBOARD_ITEMS = []
FOREMAN_EXPORTER_VERSION = "0.0.15-dev.4"
FOREMAN_VERSION = None

R_API_DEPTH = "1000"                 # how much elements get with every request to /api/hosts

try:
    # set logging
    logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)
except NameError:
    timestamp = datetime.datetime.now()
    print(timestamp, "Logging failed, returning to defaults")

try:
    # host and uri
    if os.getenv("FOREMAN_REQUEST_URI") is not None:
        REQUEST_URI = str(os.getenv("FOREMAN_REQUEST_URI"))
        if not REQUEST_URI.endswith("/"):
            REQUEST_URI += "/"
    else:
        REQUEST_URI = "https://foreman.sample.com/"
    # display variables
    REQUEST_HOSTNAME = (urllib.parse.urlparse(REQUEST_URI)).netloc
    print(f"REQUEST_URI        = {REQUEST_URI}")
    print(f"REQUEST_HOSTNAME   = {REQUEST_HOSTNAME}")
    # user
    if os.getenv("FOREMAN_REQUEST_USER") is not None:
        REQUEST_USER = str(os.getenv("FOREMAN_REQUEST_USER"))
    else:
        REQUEST_USER = "api"
    print(f"REQUEST_USER       = {REQUEST_USER}")
    # password
    if os.getenv("FOREMAN_REQUEST_PASSWORD") is not None:
        REQUEST_PASSWORD = str(os.getenv("FOREMAN_REQUEST_PASSWORD"))
    else:
        REQUEST_PASSWORD = "api"
    # tls_verify
    if os.getenv("FOREMAN_REQUEST_TLS_VERIFY") is not None:
        REQUEST_TLS_VERIFY = bool(distutils.util.strtobool((os.getenv("FOREMAN_REQUEST_TLS_VERIFY"))))
    else:
        REQUEST_TLS_VERIFY = False
    print(f"REQUEST_TLS_VERIFY = {REQUEST_TLS_VERIFY}")
    # request timeout
    if os.getenv("FOREMAN_REQUEST_TIMEOUT") is not None:
        REQUEST_TIMEOUT = int(os.getenv("FOREMAN_REQUEST_TIMEOUT"))
    else:
        REQUEST_TIMEOUT = 15
    print(f"REQUEST_TIMEOUT    = {REQUEST_TIMEOUT}")
    # request interval
    if os.getenv("FOREMAN_REQUEST_INTERVAL") is not None:
        REQUEST_INTERVAL = int(os.getenv("FOREMAN_REQUEST_INTERVAL"))
    else:
        REQUEST_INTERVAL = 30
    print(f"REQUEST_INTERVAL   = {REQUEST_INTERVAL}")
except NameError:
    timestamp = datetime.datetime.now()
    print(timestamp, "Evaluation of Environmental Variables failed, returning to defaults")

if all(v_check is not None for v_check in [REQUEST_URI, REQUEST_HOSTNAME, REQUEST_USER, REQUEST_PASSWORD, REQUEST_TLS_VERIFY, REQUEST_TIMEOUT, REQUEST_INTERVAL]):
    pass
else:
    timestamp = datetime.datetime.now()
    print(timestamp, "One of variables is empty")
    raise SystemExit(1)


# initial data
def f_requests_status():
    ''' Process Foreman's status response '''
    global FOREMAN_STATUS_RESPONSE
    global FOREMAN_STATUS_BODY
    global R_API_DEPTH
    try:
        response = httpx.get(REQUEST_URI+'api/status', auth=(REQUEST_USER, REQUEST_PASSWORD), verify=REQUEST_TLS_VERIFY, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        try:
            body = json.loads(response.text)
        except JSONDecodeError:
            print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/status failed, response is not json")
            time.sleep(1)
            sys.exit()
        if 200 >= response.status_code <= 399:
            print(datetime.datetime.now(), f"Status request at {REQUEST_URI}api/status with code {response.status_code} took {response.elapsed.seconds} seconds")
            FOREMAN_STATUS_BODY = body
            FOREMAN_STATUS_RESPONSE = response
            # Status section
            if FOREMAN_STATUS_BODY['version'] is not None:
                r_status_version = str(FOREMAN_STATUS_BODY['version'])
                print(datetime.datetime.now(), f"Foreman version found at: {REQUEST_URI} is {r_status_version}")
                # since version 2.2.0 pagination can be set to all or number
                if version.parse(r_status_version) > version.parse("2.2.0"):
                    R_API_DEPTH = "all"
            else:
                pass
        else:
            print(datetime.datetime.now(), f"Response code not proper: {response.status_code}")
    except httpx.HTTPStatusError as err:
        print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/status failed with code {err}")
        time.sleep(1)


def f_requests_hosts():
    ''' Process Foreman's hosts response '''
    global FOREMAN_HOSTS_RESPONSE
    global FOREMAN_HOSTS_BODY
    try:
        response = httpx.get(REQUEST_URI+'api/hosts?per_page='+str(R_API_DEPTH), auth=(REQUEST_USER, REQUEST_PASSWORD), verify=REQUEST_TLS_VERIFY, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        try:
            body = json.loads(response.text)
        except JSONDecodeError:
            print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/hosts failed, response is not json")
            time.sleep(1)
            sys.exit()
        if 200 >= response.status_code <= 399:
            print(datetime.datetime.now(), f"Hosts request at {REQUEST_URI}api/hosts with code {response.status_code} took {response.elapsed.seconds} seconds")
            FOREMAN_HOSTS_BODY = body
            FOREMAN_HOSTS_RESPONSE = response
        else:
            print(datetime.datetime.now(), f"Response code not proper: {response.status_code}")
    except httpx.HTTPStatusError as err:
        print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/hosts failed with code {err}")
        time.sleep(1)


def f_requests_dashboard():
    ''' Process Foreman's dashboard response '''
    global FOREMAN_DASHBOARD_RESPONSE
    global FOREMAN_DASHBOARD_BODY
    try:
        response = httpx.get(REQUEST_URI+'api/dashboard?per_page=10000', auth=(REQUEST_USER, REQUEST_PASSWORD), verify=REQUEST_TLS_VERIFY, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        try:
            body = json.loads(response.text)
        except JSONDecodeError:
            print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/dashboard failed, response is not json")
            time.sleep(1)
            sys.exit()
        if 200 >= response.status_code <= 399:
            print(datetime.datetime.now(), f"Dashboard request at: {REQUEST_URI}api/dashboard with code {response.status_code} took {response.elapsed.seconds} seconds")
            FOREMAN_DASHBOARD_BODY = body
            FOREMAN_DASHBOARD_RESPONSE = response
        else:
            print(datetime.datetime.now(), f"Response code not proper:  {response.status_code}")
    except httpx.HTTPStatusError as err:
        print(datetime.datetime.now(), f"Request at: {REQUEST_URI}api/dashboard failed with code {err}")
        time.sleep(1)


# register class
class RequestsHosts:
    ''' Register Prometheus Metrics for Foremant's hosts '''
    def __init__(self):
        pass

    @staticmethod
    def collect():
        ''' Register Prometheus Metrics for Foreman's hosts '''
        # foreman gauges
        g_hosts = GaugeMetricFamily("foreman_exporter_hosts", 'foreman host status', labels=['hostname', 'domain', 'configuration', 'configuration_label',
                                    'puppet_status', 'global_label', 'puppet_environment', 'operatingsystem', 'foreman_hostname'])
        if FOREMAN_HOSTS_BODY is not None:
            for each in FOREMAN_HOSTS_BODY['results']:
                # Name - let's skip processing if field is None
                if each.get('name') is None:
                    continue
                name = str(each['name'])
                # domain
                domain = str(each['domain_name']) if each.get('domain_name') else 'unknown'
                # status
                status = str(each.get('global_status', '199'))
                # Global status
                global_label = str(each.get('global_status_label', 'unknown'))
                # Configuration status
                configuration_status = str(each.get('configuration_status', '199'))
                # Configuration status label
                configuration_status_label = str(each.get('configuration_status_label', 'unknown'))
                # Puppet status
                puppet_status = str(each.get('puppet_status', '199'))
                # Environment
                environment_name = str(each.get('environment_name', 'unknown'))
                # Operatingsystem
                operatingsystem = str(each.get('operatingsystem_name', 'unknown'))
                
                g_hosts.add_metric([name, domain, configuration_status, configuration_status_label, puppet_status, global_label,
                                    environment_name, operatingsystem, REQUEST_HOSTNAME], status)
            yield g_hosts
        else:
            pass

        # How long the process was made
        if FOREMAN_HOSTS_RESPONSE is not None:
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


class RequestsDashboard:
    ''' Register Prometheus Metrics for Foremant's Dashboards '''
    def __init__(self):
        pass

    @staticmethod
    def collect():
        ''' Register Prometheus Metrics for Foremant's Dashboards '''
        # Dashboard section
        g_dashboard = {}
        FOREMAN_DASHBOARD_ITEMS.clear()
        if FOREMAN_DASHBOARD_BODY is not None:
            for each in FOREMAN_DASHBOARD_BODY:
                FOREMAN_DASHBOARD_ITEMS.append(each)
                # total hosts
            if FOREMAN_DASHBOARD_ITEMS is not None:
                for each in FOREMAN_DASHBOARD_ITEMS:
                    if each != 'glossary':
                        g_dashboard[each] = GaugeMetricFamily("foreman_exporter_dashboard_"+each, FOREMAN_DASHBOARD_BODY['glossary'][each], labels=['foreman_hostname'])
                        g_dashboard[each].add_metric([REQUEST_HOSTNAME], int(FOREMAN_DASHBOARD_BODY[each]))
                        yield g_dashboard[each]
        else:
            pass
        # How long the process (request dashboard) was made
        if FOREMAN_DASHBOARD_RESPONSE is not None:
            g_dashboard_time = GaugeMetricFamily("foreman_exporter_dashboard_request_time_seconds", 'foreman dashboard request time seconds', labels=['foreman_hostname'])
            g_dashboard_time.add_metric([REQUEST_HOSTNAME], int(FOREMAN_DASHBOARD_RESPONSE.elapsed.seconds))
            yield g_dashboard_time
        else:
            pass


class RequestsStatus:
    ''' Register Prometheus Metrics for Foreman's Status '''
    def __init__(self):
        pass

    @staticmethod
    def collect():
        ''' Register Prometheus Metrics for Foremant's Status '''
#        global R_API_DEPTH
        # How long the process (request dashboard) was made
        if FOREMAN_STATUS_RESPONSE is not None:
            g_status_time = GaugeMetricFamily("foreman_exporter_status_request_time_seconds", 'foreman status request time seconds', labels=['foreman_hostname'])
            g_status_time.add_metric([REQUEST_HOSTNAME], int(FOREMAN_STATUS_RESPONSE.elapsed.seconds))
            yield g_status_time
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
    print(datetime.datetime.now(), "Starting http server at port 8000")
    # Start up the server to expose the metrics.
    start_http_server(8000)


def main():
    ''' Main threading loop '''
    thread = threading.Thread(target=f_process_request)
    thread.start()
    thread.join()
    f_requests_status()
    f_requests_hosts()
    f_requests_dashboard()
    f_process_request()


if __name__ == '__main__':
    # Initial fill in
    f_requests_status()
    f_requests_hosts()
    f_requests_dashboard()
    print(datetime.datetime.now(), f"Script version is {FOREMAN_EXPORTER_VERSION}")
    f_start_http()
    # Register gauges
    REGISTRY.register(RequestsHosts())
    REGISTRY.register(RequestsDashboard())
    REGISTRY.register(RequestsStatus())
    while True:
        main()
