# Cachet Uptime Robot

Cachet is an open source status page system, this repository is a Python script that gets data from Uptime Robot and updates uptime metric in Cachet.

### Getting started 

To get started, you have to specify your Cachet settings and UptimeRobot api key.
```python
UPTIME_ROBOT_API_KEY = 'your-api-key'
```


```python 
# Specify variables for each Status Page you want to setup.
monitors_map = {
    'https://mydomain.com': {
        'api_key': 'cachet-api-key',
        'status_url': 'https://your-status-page-url.com',
        'component_id': 1,
        'metric_id': 1,
    }
}
```

* `api_key`:  Global Cachet API key
* `status_url`: URL of the status page your setting up. (Used to push using the API)
* `component_id`: Id of the Cachet component with site status
* `metric_id`: Id of the uptime metric in your Cachet installation

### Usage

Run this python script using a cron job.
```python

# Create a monitor instance 
m = Monitor()

# Gets uptime data from UptimeRobot and send to Cachet.
m.update_all_monitors()
```
