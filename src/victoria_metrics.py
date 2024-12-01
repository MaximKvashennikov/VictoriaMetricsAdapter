import json
import allure
import requests
from random import randint
from datetime import datetime, timedelta
from typing import List, Tuple, Union
from src.config.settings import settings
from src.helpers.retry_helper import RetryHelper
from src.models.metric_models import ExampleMetricLabel, ExampleMetricData, BaseMetricLabel


class VictoriaMetricsClient:
    SERIES = '/prometheus/api/v1/series'
    QUERY_RANGE = '/prometheus/api/v1/query_range'
    IMPORT = '/api/v1/import'
    DELETE_SERIES = '/api/v1/admin/tsdb/delete_series'

    def __init__(self):
        self.url = settings.url
        self.session = requests.Session()
        self.session.auth = (settings.vm_user, settings.vm_user)
        self.session.verify = False

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        response = self.session.request(method, self.url + endpoint, **kwargs)
        response.raise_for_status()
        return response

    def _ensure_metrics_deleted(self, metric: list) -> None:
        RetryHelper(
            max_retries=3,
            delay=2.0,
            retry_condition=lambda response: not response.get('data'),
        ).execute(self.victoria_get_metrics, metric)

    def _ensure_metric_range_data_exist(self, params: dict) -> list:
        result = RetryHelper(
            max_retries=5,
            delay=3.0,
            retry_condition=lambda response: response.json().get('data', {}).get('result'),
        ).execute(self._request, 'GET', self.QUERY_RANGE, params=params)
        return result.json()['data']['result']

    @allure.step('Importing data into VictoriaMetrics')
    def victoria_import(self, data: dict) -> None:
        self._request('POST', self.IMPORT, data=json.dumps(data))

    @allure.step('Deleting time series in VictoriaMetrics')
    def victoria_delete_metric(self, metrics: list) -> None:
        self._request('POST', self.DELETE_SERIES, params={'match[]': metrics})
        self._ensure_metrics_deleted(metrics)

    @allure.step('Retrieving metric data from VictoriaMetrics')
    def victoria_get_metrics(self, metrics: list) -> dict:
        response = self._request('GET', self.SERIES, params={'match[]': metrics})
        return response.json()

    @allure.step('Retrieving metric data for a specific time range from VictoriaMetrics')
    def get_metric_range_data(
            self,
            metrics: list,
            step: int = 60,
            start: datetime = datetime.now() - timedelta(hours=1),
            end: datetime = datetime.now()
    ) -> list:

        return self._ensure_metric_range_data_exist(
            params={
                'query': f'{{__name__=~"{'|'.join(metrics)}"}}',
                'start': start.timestamp(),
                'end': end.timestamp(),
                'step': step
            }
        )

    @staticmethod
    def generate_timestamps_and_values(
            start: datetime = datetime.now() - timedelta(minutes=60),
            end: datetime = datetime.now(),
            step: int = 60,
            value: Union[int, float] = None,
            min_value: int = 0,
            max_value: int = 1000
    ) -> Tuple[List[int], List[int | float]]:
        """
        Generates a time series and corresponding values for metrics.

        :param step: Step interval in seconds
        :param start: Start of the interval in datetime format
        :param end: End of the interval in datetime format, default is current datetime
        :param value: Value to generate for the entire series,
        default is random within min_value - max_value
        :param min_value: Minimum value for random range
        :param max_value: Maximum value for random range
        """
        current_time = start
        timestamps = []

        while current_time < end:
            timestamps.append(int(current_time.timestamp() * 1000))
            current_time += timedelta(seconds=step)

        if value is None:
            values = [randint(min_value, max_value) for _ in timestamps]
        else:
            values = [value for _ in timestamps]

        return timestamps, values

    @allure.step('Importing a specific metric into VictoriaMetrics')
    def victoria_import_concrete_metric(
            self,
            metric_label: BaseMetricLabel,
            start: datetime = datetime.now() - timedelta(minutes=60),
            end: datetime = datetime.now(),
            step: int = 60,
            value: Union[int, float] = None,
            min_value: int = 0,
            max_value: int = 1000,
            delete_metrics_first: bool = True
    ) -> None:
        """
        Imports a specific metric into VictoriaMetrics.
        :param metric_label: MetricLabel object that contains the metric and corresponding values.
        :param step: Step interval in seconds
        :param start: Start of the interval in datetime format
        :param end: End of the interval in datetime format, default is current datetime
        :param value: Value to generate for the entire series,
        default is random within min_value - max_value
        :param min_value: Minimum value for random range
        :param max_value: Maximum value for random range
        :param delete_metrics_first: Flag to delete old series before importing, default is True
        """
        timestamps, values = self.generate_timestamps_and_values(
            start=start,
            end=end,
            step=step,
            value=value,
            min_value=min_value,
            max_value=max_value
        )

        metric_data = ExampleMetricData(
            metric=metric_label,
            values=values,
            timestamps=timestamps
        )

        if delete_metrics_first:
            data_for_delete = f'{metric_data.metric.metric_name}'
            self.victoria_delete_metric([data_for_delete])

        self.victoria_import(metric_data.model_dump(by_alias=True, exclude_none=True))


if __name__ == "__main__":
    """
    Example usage of the VictoriaMetricsClient class:
    - Deletes an existing metric.
    - Imports example metrics.
    - Retrieves metric range data.
    """

    example_metric_data_one = ExampleMetricLabel(
        metric_name='test_metric_1',
        security='Unsafe',
        step_count='5',
        risk_name='1C'
    )

    example_metric_data_two = ExampleMetricLabel(
        metric_name='test_metric_2',
        security='Safe',
    )

    vm = VictoriaMetricsClient()
    vm.victoria_delete_metric(['test_metric'])

    vm.victoria_import_concrete_metric(
        metric_label=example_metric_data_one,
        value=30,
        start=datetime.now() - timedelta(hours=3),
    )

    vm.victoria_import_concrete_metric(
        metric_label=example_metric_data_two,
    )

    print(vm.get_metric_range_data(metrics=['test_metric_1', 'test_metric_2']))
