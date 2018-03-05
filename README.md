# Cachet Uptime Robot

Cachet is an open source status page system, this repository is a Python script that does two things, **first**, it reads the status of a page in UptimeRobot and updates a cachet component based on that status and **second**, it updates a metric with the historic uptime ratio from Uptime Robot.

**Component status**

| Uptime Robot | Cachet |
| --- | --- |
| Not checked yet | Operational |
| Up | Operational |
| Seems down | Partial outage |
| Down | Major outage |

### Getting started 

To get started, you have to specify your Cachet and UptimeRobot settings and in **config.ini**.
```ini
[uptimeRobot] // Global uptimerobot API
UptimeRobotMainApiKey = your-api-key

[cachet] // Global cachet status API
CachetApiKey = cachet-api-key
CachetUrl = https://status.mycompany.com

[uptimeRobotMonitorID1] // This will update ComponentId 1 on the global Cachet
ComponentId = 1

[uptimeRobotMonitorID2] // Still possible to use custom cachet settings 
CachetApiKey = cachet-api-key
CachetUrl = https://status.mycompany.com
MetricId = 1
ComponentId = 1
```

* `UptimeRobotMainApiKey`: UptimeRobot API key.
* `uptimeRobotMetricID`: This exact "monitor" id set in UptimeRobot. You can find the id's by running `python update_status.py config.ini getIds`
* `CachetApiKey`:  Cachet API key.
* `CachetUrl`: URL of the API of the status page you want to show the site availability in.
* `MetricId`: (Optional) Id of the Cachet metric with site availability.
* `ComponentId`: (Optional) Id of the component you want to update on each check.

Either `MetricId` or `ComponentId` must be defined per `uptimeRobotMonitorID`

MetricId is special, it will try to sync the graph from UptimeRobot to Cachet. Please keep this in mind at all times.

### Usage

Register a cron that runs `update_status.py` every 5 minutes.

```bash
# Open cron file to edit.
crontab -e
```

Edit the crontab file and add this line:
```bash
*/5 * * * * python ~/path/update_status.py ~/path/config.ini
```

_Note that the path of the update_status.py & config.ini files may vary depending on the location you cloned the repository_

### Running manually

You can also update your Cachet data manually by running this:

```python
python update_status.py config.ini

>>> Updating monitor MySite. URL: http://mysite.co. ID: 12345678
>>> Metric created: {'data': {'calculated_value': 99.99, 'counter': 1, 'metric_id': 4, 'value': 99.99, 'created_at': '2016-08-12 08:23:10', 'updated_at': '2016-08-12 08:23:10', 'id': 99}}
```
