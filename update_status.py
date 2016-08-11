#!/usr/bin/env python3
import json
import sys
import configparser
from urllib import request
from urllib import parse
from datetime import datetime


class UptimeRobot(object):
    """ Intermediate class for setting uptime stats.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.uptimerobot.com/'

    def get_monitors(self, response_times=0, logs=0, uptime_ratio=''):
        """
        Returns status and response payload for all known monitors.
        """
        url = self.base_url
        url += 'getMonitors?apiKey={0}'.format(self.api_key)
        url += '&noJsonCallback=1&format=json'

        # responseTimes - optional (defines if the response time data of each
        # monitor will be returned. Should be set to 1 for getting them.
        # Default is 0)
        if response_times:
            url += '&responseTimes=1'

        # logs - optional (defines if the logs of each monitor will be
        # returned. Should be set to 1 for getting the logs. Default is 0)
        if logs:
            url += '&logs=1'

        # customUptimeRatio - optional (defines the number of days to calculate
        # the uptime ratio(s) for. Ex: customUptimeRatio=7-30-45 to get the
        # uptime ratios for those periods)
        if uptime_ratio:
            url += '&customUptimeRatio={0}'.format(uptime_ratio)

        # Verifying in the response is jsonp in otherwise is error
        response = request.urlopen(url)
        content = response.read().decode('utf-8')
        j_content = json.loads(content)
        if j_content.get('stat'):
            stat = j_content.get('stat')
            if stat == "ok":
                return True, j_content
        return False, j_content


class CachetHq(object):
    # Uptime Robot status list
    UPTIME_ROBOT_PAUSED = 0
    UPTIME_ROBOT_NOT_CHECKED_YET = 1
    UPTIME_ROBOT_UP = 2
    UPTIME_ROBOT_SEEMS_DOWN = 8
    UPTIME_ROBOT_DOWN = 9

    # Cachet status list
    CACHET_OPERATIONAL = 1
    CACHET_PERFORMANCE_ISSUES = 2
    CACHET_SEEMS_DOWN = 3
    CACHET_DOWN = 4

    def __init__(self, cachet_api_key, cachet_url):
        self.cachet_api_key = cachet_api_key
        self.cachet_url = cachet_url

    def update_component(self, id_component=1, status=None):
        component_status = None

        # Not Checked yet and Up
        if status in [self.UPTIME_ROBOT_NOT_CHECKED_YET, self.UPTIME_ROBOT_UP]:
            component_status = self.CACHET_OPERATIONAL

        # Seems down
        elif status == self.UPTIME_ROBOT_SEEMS_DOWN:
            component_status = self.CACHET_SEEMS_DOWN

        # Down
        elif status == self.UPTIME_ROBOT_DOWN:
            component_status = self.CACHET_DOWN

        if component_status:
            url = '{0}/{1}/{2}/'.format(
                self.cachet_url,
                'components',
                id_component
            )
            data = parse.urlencode({
                'status': component_status,
            }).encode('utf-8')
            req = request.Request(
                url=url,
                data=data,
                method='PUT',
                headers={'X-Cachet-Token': self.cachet_api_key},
            )
            response = request.urlopen(req)
            content = response.read().decode('utf-8')
            return content

    def set_data_metrics(self, value, timestamp, id_metric=1):
        url = '{0}/metrics/{1}/points/'.format(self.cachet_url, id_metric)
        data = parse.urlencode({
            'value': value,
            'timestamp': timestamp,
        }).encode('utf-8')
        req = request.Request(
            url=url,
            data=data,
            method='POST',
            headers={'X-Cachet-Token': self.cachet_api_key},
        )
        response = request.urlopen(req)

        return json.loads(response.read().decode('utf-8'))

    def get_last_metric_point(self, id_metric):
        url = '{0}/metrics/{1}/points/'.format(self.cachet_url, id_metric)
        req = request.Request(
            url=url,
            method='GET',
            headers={
                'X-Cachet-Token': self.cachet_api_key,
            }
        )
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        last_page = json.loads(
            content
        ).get('meta').get('pagination').get('total_pages')

        url = '{0}/metrics/{1}/points?page={2}'.format(
            self.cachet_url,
            id_metric,
            last_page
        )

        req = request.Request(
            url=url,
            method='GET',
            headers={'X-Cachet-Token': self.cachet_api_key},
        )
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        if json.loads(content).get('data'):
            data = json.loads(content).get('data')[0]
        else:
            data = {
                'created_at': datetime.now().date().strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
            }

        return data


class Monitor(object):
    def __init__(self, monitor_list, api_key):
        self.monitor_list = monitor_list
        self.api_key = api_key

    def send_data_to_catchet(self, monitor):
        """ Posts data to Cachet API.
            Data sent is the value of last `Uptime`.
        """
        try:
            website_config = self.monitor_list[monitor.get('url')]
        except KeyError:
            print('ERROR: monitor is not valid')
            sys.exit(1)

        cachet = CachetHq(
            cachet_api_key=website_config['api_key'],
            cachet_url=website_config['status_url'],
        )

        cachet.update_component(
            website_config['component_id'],
            monitor.get('status')
        )

        last_date_metric_point = datetime.strptime(
            cachet.get_last_metric_point(
                website_config['metric_id']
            ).get('created_at'), '%Y-%m-%d %H:%M:%S')

        for point in reversed(monitor.get('responsetime')):
            point_datetime = datetime.strptime(
                point.get('datetime'),
                '%m/%d/%Y %H:%M:%S'
            )
            if point_datetime > last_date_metric_point:
                metric = cachet.set_data_metrics(
                    point.get('value'),
                    int(point_datetime.strftime('%s')),
                    website_config['metric_id']
                )
                print('Metric created: {0}'.format(metric))

    def update(self):
        """ Update all monitors uptime and status.
        """
        uptime_robot = UptimeRobot(self.api_key)
        success, response = uptime_robot.get_monitors(response_times=1)
        if success:
            monitors = response.get('monitors').get('monitor')
            for monitor in monitors:
                print('Updating monitor {0}. URL: {1}. ID: {2}'.format(
                    monitor['friendlyname'],
                    monitor['url'],
                    monitor['id'],
                ))
                self.send_data_to_catchet(monitor)
        else:
            print('ERROR: No data was returned from UptimeMonitor')


if __name__ == "__main__":
    CONFIG = configparser.ConfigParser()
    CONFIG.read(sys.argv[1])
    SECTIONS = CONFIG.sections()

    if not SECTIONS:
        print('ERROR: File path is not valid')
        sys.exit(1)

    UPTIME_ROBOT_API_KEY = None
    MONITOR_DICT = {}
    for element in SECTIONS:
        if element == 'uptimeRobot':
            uptime_robot_api_key = CONFIG[element]['UptimeRobotMainApiKey']
        else:
            MONITOR_DICT[element] = {
                'cachet_api_key': CONFIG[element]['CachetApiKey'],
                'cachet_url': CONFIG[element]['CachetUrl'],
                'metric_id': CONFIG[element]['MetricId'],
            }

    MONITOR = Monitor(monitor_list=MONITOR_DICT, api_key=uptime_robot_api_key)
    MONITOR.update()
