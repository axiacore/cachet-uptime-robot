import unittest.mock as mock
import pytest
import update_status


class TestMonitor(object):
    def test_send_data_to_cachet_updates_the_component_status(self, monitor, uptimerobot_monitor):
        website_config = monitor.monitor_list[uptimerobot_monitor['id']]

        with mock.patch('update_status.CachetHq') as cachet:
            monitor.sync_metric = lambda x, y: None
            monitor.send_data_to_cachet(uptimerobot_monitor)

        cachet().update_component.assert_called_with(
            website_config['component_id'],
            int(uptimerobot_monitor['status'])
        )

    @pytest.mark.skip
    def test_send_data_to_cachet_updates_data_metrics(self, monitor, uptimerobot_monitor):
        website_config = monitor.monitor_list[uptimerobot_monitor['id']]

        with mock.patch('update_status.CachetHq') as cachet:
            monitor.sync_metric = lambda x, y: None
            monitor.send_data_to_cachet(uptimerobot_monitor)

        cachet().set_data_metrics.assert_called_with(
            uptimerobot_monitor['custom_uptime_ratio'],
            mock.ANY,
            website_config['metric_id']
        )

    def test_sync_metric(self, monitor, cachet, uptimerobot_monitor, cachet_metric):
        future_date = 999999999999
        cachet_metric['created_at'] = '2017-01-01 00:00:00'
        cachet_metric_unixtime = 1483228800

        cachet_mock = mock.create_autospec(cachet)
        cachet_mock.get_last_metric_point.return_value = cachet_metric

        assert len(uptimerobot_monitor['response_times']) >= 3, \
            'We need at least 3 response times to run the tests'

        uptimerobot_monitor['response_times'][-1]['datetime'] = future_date
        uptimerobot_monitor['response_times'][-2]['datetime'] = future_date

        monitor.sync_metric(uptimerobot_monitor, cachet_mock)

        expected_response_times = [
            x for x in uptimerobot_monitor['response_times']
            if x['datetime'] > cachet_metric_unixtime
        ]

        assert cachet_mock.set_data_metrics.call_count == len(expected_response_times)
        for response_time in expected_response_times:
            cachet_mock.set_data_metrics.assert_any_call(
                response_time['value'],
                response_time['datetime'],
                mock.ANY
            )


@pytest.fixture
def monitor_list():
    return {
        '6516846': {
            'cachet_api_key': 'CACHET_API_KEY',
            'cachet_url': 'http://status.example.org',
            'metric_id': '1',
            'component_id': '1',
        },
    }


@pytest.fixture
def cachet_metric():
    return {
        'id': 1,
        'metric_id': 1,
        'value': 100,
        'created_at': '2017-08-25 17:17:14',
        'updated_at': '2017-08-25 17:17:14',
        'counter': 1,
        'calculated_value': 100,
    }


@pytest.fixture
def uptimerobot_monitor(monitor_list):
    monitors_ids = [m for m in monitor_list.keys()]
    id = monitors_ids[0]

    return {
        'url': 'monitor_url',
        'friendly_name': 'friendly_name',
        'id': id,
        'status': '2',  # UP,
        'custom_uptime_ratio': '100',
        'response_times': [
            {'datetime': 1, 'value': 609},
            {'datetime': 2, 'value': 625},
            {'datetime': 3, 'value': 687},
            {'datetime': 4, 'value': 750},
            {'datetime': 5, 'value': 750},
            {'datetime': 6, 'value': 922},
        ]
    }


@pytest.fixture
def monitor(monitor_list):
    api_key = 'UPTIME_ROBOT_API_KEY'
    return update_status.Monitor(monitor_list, api_key)


@pytest.fixture
def cachet():
    return update_status.CachetHq(
        cachet_api_key='CACHET_API_KEY',
        cachet_url='CACHET_URL'
    )
