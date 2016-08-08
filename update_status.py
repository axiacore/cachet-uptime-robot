import json
from urllib import request
from urllib import parse
from datetime import datetime


class UptimeRobot(object):
    """ Intermediate class for setting uptime stats.
    """
    def __init__(self, api_key=''):
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

    def __init__(self, api_key='', base_url='http://localhost/api/v1'):
        self.api_key = api_key
        self.base_url = base_url

    def update_component(self, id_component=1, status=None):
        """"""
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
                self.base_url,
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
                headers={
                    'X-Cachet-Token': self.api_key,
                }
            )
            response = request.urlopen(req)
            content = response.read().decode('utf-8')
            return content

    def set_data_metrics(self, value, timestamp, id_metric=1):
        url = '{0}/metrics/{1}/points/'.format(self.base_url, id_metric)
        data = parse.urlencode({
            'value': value,
            'timestamp': timestamp,
        }).encode('utf-8')
        req = request.Request(
            url=url,
            data=data,
            method='POST',
            headers={
                'X-Cachet-Token': self.api_key,
            }
        )
        response = request.urlopen(req)
        content = response.read().decode('utf-8')
        return content

    def get_last_metric_point(self, id_metric):
        url = '{0}/metrics/{1}/points/'.format(self.base_url, id_metric)
        req = request.Request(
            url=url,
            method='GET',
            headers={
                'X-Cachet-Token': self.api_key,
            }
        )
        response = request.urlopen(req)
        content = response.read().decode('utf-8')

        last_page = json.loads(
            content
        ).get('meta').get('pagination').get('total_pages')

        url = '{0}/metrics/{1}/points?page={2}'.format(
            self.base_url,
            id_metric,
            last_page
        )

        req = request.Request(
            url=url,
            method='GET',
            headers={
                'X-Cachet-Token': self.api_key,
            }
        )
        response = request.urlopen(req)
        content = response.read().decode('utf-8')
        return json.loads(content).get('data')[-1]


class Monitor(object):
    monitors_map = {
        'https://mydomain.com': {
            'api_key': 'cachet-api-key',
            'status_url': 'https://your-status-page-url.com',
            'component_id': 1,
            'metric_id': 1,
        }
    }

    def send_data_to_catchet(self, monitor):
        """ Posts data to Cachet API.
            Data sent is the value of last `Uptime`.
        """
        website_config = self.monitors_map[monitor.get('url')]
        cachet = CachetHq(
            website_config['api_key'],
            website_config['status_url']
        )

        cachet.update_component(
            website_config['component_id'],
            monitor.get('status')
        )

        last_date_metric_point = datetime.strptime(
            cachet.get_last_metric_point(
                website_config['metric_id']
            ).get('created_at'), '%Y-%m-%d %H:%M:%S')

        print(last_date_metric_point)

        for point in reversed(monitor.get('responsetime')):
            point_datetime = datetime.strptime(
                point.get('datetime'),
                '%d/%m/%Y %H:%M:%S'
            )
            if point_datetime > last_date_metric_point:
                print(cachet.set_data_metrics(
                    point.get('value'),
                    int(point_datetime.strftime('%s')),
                    website_config['metric_id']
                ))

    def update_all_monitors(self):
        """ Update all monitors uptime and status.
        """
        uptime_robot = UptimeRobot()
        success, response = uptime_robot.get_monitors(response_times=1)
        if success:
            monitors = response.get('monitors').get('monitor')
            for monitor in monitors:
                self.send_data_to_catchet(monitor)
