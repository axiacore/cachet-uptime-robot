# Cachet Uptime Robot

Cachet is an open source status page system, this repository is a Python script that does two things, **first**, it reads the status of a page in UptimeRobot and updates a cachet component based on that status and **second**, it updates a metric with the historic uptime data from Uptime Robot.

**Component status: Uptime Robot (left), Cachet (right)**

* Not checked yet: Operational
* Up: Operational
* Seems down: Partial outage
* Down: Major outage

### Getting started 

To get started, you have to specify your Cachet settings and UptimeRobot api key.
```python
UPTIME_ROBOT_API_KEY = 'your-api-key'
```

In the `MONITOR_LIST` variable you have to specify some settings for each monitor. 

```python 
MONITOR_LIST = {
    'https://mydomain.com': {
        'api_key': 'cachet-api-key',
        'status_url': 'https://your-status-page-url.com/api/v1',
        'component_id': 1,
        'metric_id': 1,
    }
}
```

* `api_key`:  Global Cachet API key
* `status_url`: URL of the API of the status page you want to show the uptime in.
* `component_id`: Id of the Cachet component with site status
* `metric_id`: Id of the metric where you want to show the uptime graph.

### Usage

Register a cron that runs `cron.py` every 5 minutes.

```bash 
# Open cron file to edit.
crontab -e
```

Edit the crontab file and add this line:
```bash
*/5 * * * * python3 ~/cachet-uptime-robot/cron.py
```

_Note that the path of cron.py may vary depending on the location you cloned the repository_

### Running manually

You can also update your Cachet data manually by running this:

```python
from update_status import Monitor

# Create a monitor instance 
m = Monitor()

# Gets uptime data from UptimeRobot and send to Cachet.
m.update_all_monitors()

>>> Updating monitor MyDomain: URL: https://mydomain.com - id: 12345678
>>> Created metric with id 27:
>>> {'data': {'id': 27, 'calculated_value': 7872, 'value': 328, 'updated_at': '2016-08-11 08:35:32', 'created_at': '2016-08-11 09:59:59', 'counter': 24, 'metric_id': 1}}
>>> ...
```
