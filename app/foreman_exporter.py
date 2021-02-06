#!/bin/python3

import os
import json
import requests
import random
import time
import datetime
import distutils.core
import urllib.parse
from prometheus_client.core import GaugeMetricFamily,CounterMetricFamily,REGISTRY
from prometheus_client import start_http_server, Summary, Counter, Histogram,Gauge

#Variables
body=None
response=None

try:
  if os.getenv("FOREMAN_REQUEST_URI") is not None:
    request_uri=str(os.getenv("FOREMAN_REQUEST_URI")+'/api/hosts/')
    request_hostname=(urllib.parse.urlparse(request_uri)).netloc
  else:
    request_uri="https://foreman.sample.com/api/hosts"
    request_hostname=(urllib.parse.urlparse(request_uri)).netloc
    pass
  if os.getenv("FOREMAN_REQUEST_USER") is not None:
    request_user=str(os.getenv("FOREMAN_REQUEST_USER"))
  else:
    request_user="api"
    pass
  if os.getenv("FOREMAN_REQUEST_PASSWORD") is not None:
    request_password=str(os.getenv("FOREMAN_REQUEST_PASSWORD"))
  else:
    request_password="api"
    pass
  if os.getenv("FOREMAN_REQUEST_TLS_VERIFY") is not None:
    request_tls_verify=distutils.util.strtobool((os.getenv("FOREMAN_REQUEST_TLS_VERIFY")))
  else:
    request_tls_verify=False
    pass
  if os.getenv("FOREMAN_REQUEST_TIMEOUT") is not None:
    request_timeout=int(os.getenv("FOREMAN_REQUEST_TIMEOUT"))
  else:
    request_timeout=60
    pass
  if os.getenv("FOREMAN_REQUEST_INTERVAL") is not None:
    request_interval=int(os.getenv("FOREMAN_REQUEST_INTERVAL"))
  else:
    request_interval=120
    pass
except:
  print ("Evaluation of Environmental Variables failed")
  raise

if all(v_check is not None for v_check in [request_uri,request_hostname, request_user, request_password, request_tls_verify,request_timeout,request_interval]):
  pass
else:
  print ("One of variables is empty")
  raise SystemExit(-1)

print ("Variables:")
print ('request_uri        = '+str(request_uri))
print ('request_hostname   = '+str(request_hostname))
print ('request_user       = '+str(request_user))
# getpass to hide passwords?
print ('request_password   = '+str(request_password))
print ('request_tls_verify = '+str(request_tls_verify))
print ('request_timeout    = '+str(request_timeout))
print ('request_interval   = '+str(request_interval))


# initial data
def f_requests_hosts():
  global response
  global body
  body=None
  while body is None:
    try:
      response = requests.get(request_uri,auth=(request_user,request_password),verify=request_tls_verify, timeout=request_timeout)
      body = json.loads(response.text)
      if 200 >= response.status_code <= 399:
          timestamp = datetime.datetime.now()
          print (timestamp,"Request at", request_uri, "with code", response.status_code, "took", response.elapsed.seconds, "seconds")
          pass
      else:
        print ("Response code not proper",response.status_code)
    except:
      print ("Request at", request_uri, "failed with code", response.status_code )
      time.sleep (3)
      pass

# register class
class requests_hosts:
    def __init__(self):
        pass
    def collect(self):
        g_hosts = GaugeMetricFamily("foreman_exporter_hosts", 'foreman host status', labels=['hostname','domain','configuration','configuration_label','puppet_status','global_label','environment','operatingsystem', 'foreman_hostname'])
        if body is not None:
          for each in body['results']:
            name=str(each['name'])
            domain=str(each['domain_name'])
            status=(each['global_status'])
            global_label=str(each['global_status_label'])
            configuration_status=str(each['configuration_status'])
            configuration_status_label=str(each['configuration_status_label'])
            puppet_status=str(each['puppet_status'])
            environment_name=str(each['environment_name'])
            operatingsystem=str(each['operatingsystem_name'])
            if (
                name is None or domain is None or status is None or configuration_status is None or configuration_status_label is None
               ):
              continue
            else:
              if global_label is None:
                global_label='199'
              if puppet_status is None:
                puppet_status='199'
              if environment_name is None:
                environment_name='unknown'
              if operatingsystem is None:
                operatingsystem='unknown'
              g_hosts.add_metric([name,domain,configuration_status,configuration_status_label,puppet_status,global_label,environment_name,operatingsystem,request_hostname], status)
          yield g_hosts
        else:
          pass
        # How long the process was made
        if response.elapsed.seconds is not None:
          g_hosts_time = GaugeMetricFamily("foreman_exporter_hosts_request_time_seconds", 'foreman host request time seconds',labels=['foreman_hostname'])
          g_hosts_time.add_metric([request_hostname], int(response.elapsed.seconds))
          yield g_hosts_time
        else:
          pass
        # number of hosts
        if body is not None:
          g_hosts_count=GaugeMetricFamily("foreman_exporter_hosts_count", 'foreman host count',labels=['foreman_hostname'])
          g_hosts_count.add_metric([request_hostname], int(body['total']))
          yield g_hosts_count
        else:
          pass
# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
@REQUEST_TIME.time()


def f_process_request():
    """A dummy function that takes some time."""
    time.sleep(request_interval)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    # Initial fill in
    f_requests_hosts()
    print ("Starting http server")
    start_http_server(8000)
    # Register gauges
    REGISTRY.register(requests_hosts())
    # Generate some requests.
    while True:
      f_process_request()
      f_requests_hosts()
