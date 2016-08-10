# Cachet Uptime Robot

Cachet is an open source status page system, this repository is a Python script that gets data from Uptime Robot and updates uptime metric in Cachet.

### Getting started 

To get started, you have to specify your Cachet settings and UptimeRobot api key.

```python 
monitors_map = {
    'https://mydomain.com': {
        'api_key': 'cachet-api-key',
        'status_url': 'https://your-status-page-url.com',
        'component_id': 1,
        'metric_id': 1,
    }
}
```

### Usage

Run this python script using a cron job.
```python

# Create a monitor instance 
m = Monitor()

# Gets uptime data from UptimeRobot and send to Cachet.
m.update_all_monitors()
```
