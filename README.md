# VictoriaMetricsClient

## Overview    
This repository provides a Python client for interacting with [VictoriaMetrics](https://victoriametrics.com/), a fast and scalable time-series database. The client supports importing metrics, retrieving metrics data, and deleting time-series data.

---

## Prerequisites
Before using the client, ensure you have **VictoriaMetrics** running locally or remotely.

### Run VictoriaMetrics using Docker
To start a VictoriaMetrics instance with basic authentication, execute the following command:

```bash
docker run -d --name victoria-metrics-container \
  -v victoria-metrics-data:/victoria-metrics-data \
  -p 8428:8428 \
  -e VM_AUTH_USERNAME=admin \
  -e VM_AUTH_PASSWORD=password \
  victoriametrics/victoria-metrics:latest
```
This will:

* Expose VictoriaMetrics on http://localhost:8428
* Set the username to admin and password to password

To run the client, ensure you have the following Python dependencies installed

## API Overview

#### class: `VictoriaMetricsClient`
The client interacts with VictoriaMetrics via its HTTP API.

---

### Methods

#### 1. `victoria_import(data: dict)`
Imports metrics data into VictoriaMetrics.

#### 2. `victoria_delete_metric(metrics: list)`
Deletes the specified metrics from VictoriaMetrics.

#### 3. `victoria_get_metrics(metrics: list)`
Retrieves available metrics matching the specified patterns.

#### 4. `get_metric_range_data(metrics: list, step: int, start: datetime, end: datetime)`
Retrieves metric data for a given time range.

#### 5. `victoria_import_concrete_metric(metric_label: BaseMetricLabel, ...)`
Imports a specific metric into VictoriaMetrics, with optional deletion of existing data.

![example](https://github.com/user-attachments/assets/9c31e292-607c-4267-aa2f-c397d6561fcf)
The result of running the victoria_metrics.py
