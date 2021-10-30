# Changelog

## 2021-10-30 0.0.11

* added request for `/api/status` to read foreman's version
* in case of foreman's version higher than `2.2.0` pagination counter set to `all` instead of fake number
* separation of classes to fit `Pylance` and `Pylint` tests
* more verbose logs

## 2021-09-08 0.0.10

* fixed `REQUEST_HOSTS` being empty

## 2021-09-07 0.0.9

* disabled exposing passwords in logs
* image built with latest python
* Dockerfile validation with `hadolint`

## 2021-02-18 0.0.8

* fixed pagination limits (default API and GUI limit) for requests

## 2021-02-14 0.0.7

* reworked k8s example
* added k8s example with service-monitor

## 2021-02-08 0.0.6

* added /api/dashboards to gauges
* added gauges
  * `foreman_exporter_dashboard_total_hosts`
  * `foreman_exporter_dashboard_bad_hosts`
  * `foreman_exporter_dashboard_bad_hosts_enabled`
  * `foreman_exporter_dashboard_active_hosts`
  * `foreman_exporter_dashboard_active_hosts_ok`
  * `foreman_exporter_dashboard_active_hosts_ok_enabled`
  * `foreman_exporter_dashboard_ok_hosts`
  * `foreman_exporter_dashboard_ok_hosts_enabled`
  * `foreman_exporter_dashboard_disabled_hosts`
  * `foreman_exporter_dashboard_pending_hosts`
  * `foreman_exporter_dashboard_pending_hosts_enabled`
  * `foreman_exporter_dashboard_out_of_sync_hosts`
  * `foreman_exporter_dashboard_out_of_sync_hosts_enabled`
  * `foreman_exporter_dashboard_good_hosts`
  * `foreman_exporter_dashboard_good_hosts_enabled`
  * `foreman_exporter_dashboard_percentage`
  * `foreman_exporter_dashboard_reports_missing`
  * `foreman_exporter_dashboard_request_time_seconds`
* rename `environment` label from hosts to `puppet_environment`)
* changed `sleep` main loop into threading

## 2021-02-07 0.0.5

* improved raise exception
* updated README.md
* print formatting

## 2021-02-07 0.0.4

* added Kubernetes usage example
* updated README.md

## 2021-02-06 0.0.3

* fixed clearing `body` variable in loop
* suppressed warnings when connecting to selfsigned page
* enabled stdout in dockerised app
* fixed global=>local variables assignement
* pylint applied
* TZ environment variable added to Dockerfile

## 2021-02-06 0.0.2

* fixed `TypeError: 'NoneType' object is not subscriptable` in `body.total` check
* added healtchecks to Dockerfile

## 2021-02-06 0.0.1

* Initial commit
