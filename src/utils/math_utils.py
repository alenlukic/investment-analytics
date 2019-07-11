import math
import sys


MAX_VALUE = sys.maxsize
ZERO_CUTOFF = math.pow(10, -9)


def calculate_percentile(metric_value, ordered_metrics, num_metrics, default=50.0):
    """
    Calculate given metric's percentile.

    :param metric_value: value of the metric whose percentile to calculate.
    :param ordered_metrics: ordered list of all other values for the metric.
    :param num_metrics: the number of metrics in the list.
    :param default: the default metric value.
    :return: the metric's percentile value.
    """

    if metric_value is None:
        return default

    for i, other_value in enumerate(ordered_metrics):
        if other_value == metric_value:
            return 100.0 * i / num_metrics

    return default


def is_close_to_zero(num):
    return abs(num) < ZERO_CUTOFF
