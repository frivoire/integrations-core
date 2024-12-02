# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import datetime
import os

from datadog_checks.base.utils.time import ensure_aware_datetime
from datadog_checks.dev.fs import get_here

USE_OCTOPUS_LAB = os.environ.get("USE_OCTOPUS_LAB")
OCTOPUS_LAB_ENDPOINT = os.environ.get('OCTOPUS_LAB_ENDPOINT')
OCTOPUS_API_KEY = os.environ.get('OCTOPUS_API_KEY')
OCTOPUS_SPACE = os.environ.get('OCTOPUS_SPACE', 'Default')

COMPOSE_FILE = os.path.join(get_here(), 'docker', 'docker-compose.yaml')
INSTANCE = {'octopus_endpoint': 'http://localhost:80'}

LAB_INSTANCE = {
    'octopus_endpoint': OCTOPUS_LAB_ENDPOINT,
    'headers': {'X-Octopus-ApiKey': OCTOPUS_API_KEY},
}


BASE_TIME = ensure_aware_datetime(datetime.datetime.strptime("2024-09-23 14:45:58.888492", '%Y-%m-%d %H:%M:%S.%f'))
MOCKED_TIMESTAMPS = [BASE_TIME] * 20


ALL_METRICS = [
    "octopus_deploy.space.count",
    "octopus_deploy.project_group.count",
    "octopus_deploy.project.count",
    "octopus_deploy.deployment.count",
    "octopus_deploy.deployment.queued_time",
    "octopus_deploy.deployment.executing_time",
    "octopus_deploy.deployment.completed_time",
    "octopus_deploy.server_node.count",
    "octopus_deploy.server_node.in_maintenance_mode",
    "octopus_deploy.server_node.max_concurrent_tasks",
]

ALL_EVENTS = [
    {
        'message': 'Machine test is unhealthy',
        'tags': ['space_name:Default'],
    },
    {
        'message': 'Deploy to dev failed for new-project-from-group release 0.0.2 to dev',
        'tags': ['space_name:Default'],
    },
    {
        'message': 'Deploy to dev failed for project-new-2 release 0.0.2 to dev',
        'tags': ['space_name:Default'],
    },
]
