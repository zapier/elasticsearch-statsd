import os
import sys
import time

import requests
import statsd

VERBOSE = '-v' in sys.argv

ES_API_BASE = os.environ.get('ES_API_BASE', 'http://localhost:9200')
ES_USERNAME = os.environ.get('ES_USERNAME')
ES_PASSWORD = os.environ.get('ES_PASSWORD')

STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')
STATSD_PORT = int(os.environ.get('STATSD_PORT', '8125'))
STATSD_METRIC_FORMAT = os.environ.get(
    'STATSD_METRIC_FORMAT',
    'elasticsearch.{cluster_name}.{host}.thread_pool.{queue_name}.{stat}',
)

INTERVAL = int(os.environ.get('INTERVAL', '30')) # in seconds

statsd_client = statsd.StatsClient(STATSD_HOST, STATSD_PORT)

while True:
    response = requests.get(
        '{}/_nodes/stats'.format(ES_API_BASE),
        auth=(ES_USERNAME, ES_PASSWORD),
        verify=False,
    )
    response.raise_for_status()
    data = response.json()
    cluster_name = data['cluster_name']
    nodes = data['nodes']

    for node_id, stats in nodes.items():
        host = stats['host']
        for queue_name, lengths in stats.get('thread_pool', {}).items():
            for stat, length in lengths.items():
                metric = STATSD_METRIC_FORMAT.format(
                    cluster_name=cluster_name,
                    host=host,
                    queue_name=queue_name,
                    stat=stat,
                )
                statsd_client.gauge(metric, length)
                if VERBOSE:
                    print metric, length

    time.sleep(INTERVAL)
