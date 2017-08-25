import unittest.mock as mock
import pytest
import update_status


class TestMonitor(object):
    def test_send_data_to_cachet_updates_the_component_status(self, monitor, uptimerobot_monitor):
        website_config = monitor.monitor_list[uptimerobot_monitor['url']]

        with mock.patch('update_status.CachetHq') as cachet:
            monitor.send_data_to_cachet(uptimerobot_monitor)

        cachet().update_component.assert_called_with(
            website_config['component_id'],
            int(uptimerobot_monitor['status'])
        )

    def test_send_data_to_cachet_updates_data_metrics(self, monitor, uptimerobot_monitor):
        website_config = monitor.monitor_list[uptimerobot_monitor['url']]

        with mock.patch('update_status.CachetHq') as cachet:
            monitor.send_data_to_cachet(uptimerobot_monitor)

        cachet().set_data_metrics.assert_called_with(
            uptimerobot_monitor['custom_uptime_ratio'],
            mock.ANY,
            website_config['metric_id']
        )


@pytest.fixture
def monitor_list():
    return {
        'http://example.org': {
            'cachet_api_key': 'CACHET_API_KEY',
            'cachet_url': 'http://status.example.org',
            'metric_id': '1',
            'component_id': '1',
        },
    }


@pytest.fixture
def uptimerobot_monitor(monitor_list):
    monitors_urls = [m for m in monitor_list.keys()]
    url = monitors_urls[0]

    return {
        'url': url,
        'friendly_name': url,
        'id': 'monitor_id',
        'status': '2',  # UP,
        'custom_uptime_ratio': '100',
    }


@pytest.fixture
def monitor(monitor_list):
    api_key = 'UPTIME_ROBOT_API_KEY'
    return update_status.Monitor(monitor_list, api_key)
