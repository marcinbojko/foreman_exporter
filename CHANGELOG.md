# Changelog

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
