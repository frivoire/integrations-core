# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import datetime
from contextlib import nullcontext as does_not_raise

import mock
import pytest

from datadog_checks.dev.http import MockResponse
from datadog_checks.octopus_deploy import OctopusDeployCheck

MOCKED_TIME1 = datetime.datetime.fromisoformat("2024-09-23T14:45:00.123+00:00")
MOCKED_TIME2 = MOCKED_TIME1 + datetime.timedelta(seconds=15)


@pytest.mark.parametrize(
    ('mock_http_get', 'expected_exception', 'can_connect'),
    [
        pytest.param(
            {
                'http_error': {
                    '/api/spaces': MockResponse(status_code=500),
                }
            },
            pytest.raises(Exception, match=r'Could not connect to octopus API.*'),
            0,
            id='http error',
        ),
        pytest.param(
            {
                'mock_data': {
                    '/api/spaces': {"Items": []},
                }
            },
            does_not_raise(),
            1,
            id='http ok',
        ),
    ],
    indirect=['mock_http_get'],
)
@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_can_connect(get_current_datetime, dd_run_check, aggregator, expected_exception, can_connect):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    with expected_exception:
        dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.api.can_connect', can_connect)


@pytest.mark.parametrize(
    ('mock_http_get'),
    [
        pytest.param(
            {
                'mock_data': {
                    '/api/spaces': {"Items": []},
                }
            },
            id='empty spaces',
        ),
    ],
    indirect=['mock_http_get'],
)
@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_empty_spaces(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count', count=0)


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_one_space(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count', 1, tags=['space_id:Spaces-1', 'space_name:Default'])


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_project_groups(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-1', 'project_group_name:Default Project Group', 'space_id:Spaces-1'],
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-2', 'project_group_name:test-group', 'space_id:Spaces-1'],
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-3', 'project_group_name:hello', 'space_id:Spaces-1'],
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_projects(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project.count',
        1,
        tags=[
            'project_id:Projects-1',
            'project_name:test-api',
            'project_group_id:ProjectGroups-1',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        1,
        tags=[
            'project_id:Projects-2',
            'project_name:my-project',
            'project_group_id:ProjectGroups-1',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        1,
        tags=['project_id:Projects-3', 'project_name:test', 'project_group_id:ProjectGroups-1', 'space_id:Spaces-1'],
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        1,
        tags=['project_id:Projects-4', 'project_name:hi', 'project_group_id:ProjectGroups-2', 'space_id:Spaces-1'],
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_queued_or_running_tasks(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.deployment.count',
        1,
        tags=[
            'task_id:ServerTasks-118048',
            'task_name:Deploy',
            'task_state:Executing',
            'project_id:Projects-2',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.queued_time',
        30,
        tags=[
            'task_id:ServerTasks-118048',
            'task_name:Deploy',
            'task_state:Executing',
            'project_id:Projects-2',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.executing_time',
        150,
        tags=[
            'task_id:ServerTasks-118048',
            'task_name:Deploy',
            'task_state:Executing',
            'project_id:Projects-2',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.completed_time',
        0,
        tags=[
            'task_id:ServerTasks-118048',
            'task_name:Deploy',
            'task_state:Executing',
            'project_id:Projects-2',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.count',
        1,
        tags=[
            'task_id:ServerTasks-118055',
            'task_name:Deploy',
            'task_state:Queued',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.queued_time',
        60,
        tags=[
            'task_id:ServerTasks-118055',
            'task_name:Deploy',
            'task_state:Queued',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.executing_time',
        0,
        tags=[
            'task_id:ServerTasks-118055',
            'task_name:Deploy',
            'task_state:Queued',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.completed_time',
        0,
        tags=[
            'task_id:ServerTasks-118055',
            'task_name:Deploy',
            'task_state:Queued',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_completed_tasks(get_current_datetime, dd_run_check, aggregator):
    instance = {'octopus_endpoint': 'http://localhost:80'}
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)
    metrics = aggregator.metrics('octopus_deploy.deployment.count')
    for metric in metrics:
        assert not ('project_id:Projects-1' in metric.tags and 'task_state:Success' in metric.tags)
        assert not ('project_id:Projects-3' in metric.tags and 'task_state:Success' in metric.tags)

    get_current_datetime.return_value = MOCKED_TIME2
    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.deployment.count',
        1,
        tags=[
            'task_id:ServerTasks-1847',
            'task_name:Deploy',
            'task_state:Failed',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.queued_time',
        110,
        tags=[
            'task_id:ServerTasks-1847',
            'task_name:Deploy',
            'task_state:Failed',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.executing_time',
        50,
        tags=[
            'task_id:ServerTasks-1847',
            'task_name:Deploy',
            'task_state:Failed',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.completed_time',
        5,
        tags=[
            'task_id:ServerTasks-1847',
            'task_name:Deploy',
            'task_state:Failed',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.count',
        1,
        tags=[
            'task_id:ServerTasks-1846',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.queued_time',
        90,
        tags=[
            'task_id:ServerTasks-1846',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.executing_time',
        54,
        tags=[
            'task_id:ServerTasks-1846',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.completed_time',
        1,
        tags=[
            'task_id:ServerTasks-1846',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.count',
        tags=[
            'task_id:ServerTasks-1845',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.queued_time',
        18,
        tags=[
            'task_id:ServerTasks-1845',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.executing_time',
        41,
        tags=[
            'task_id:ServerTasks-1845',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.deployment.completed_time',
        14,
        tags=[
            'task_id:ServerTasks-1845',
            'task_name:Deploy',
            'task_state:Success',
            'project_id:Projects-3',
            'space_id:Spaces-1',
        ],
    )


@pytest.mark.parametrize(
    ('mock_http_get'),
    [
        pytest.param(
            {
                'mock_data': {
                    '/api/spaces': {
                        "Items": [
                            {
                                "Id": "Spaces-1",
                                "Name": "First",
                            },
                            {
                                "Id": "Spaces-2",
                                "Name": "Second",
                            },
                        ]
                    },
                    '/api/Spaces-1/projectgroups': {"Items": []},
                    '/api/Spaces-2/projectgroups': {"Items": []},
                }
            },
            id='empty spaces',
        ),
    ],
    indirect=['mock_http_get'],
)
@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_discovery_spaces(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'spaces': {
            'include': ['Second'],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count', tags=['space_id:Spaces-1', 'space_name:First'], count=0)
    aggregator.assert_metric('octopus_deploy.space.count', tags=['space_id:Spaces-2', 'space_name:Second'])


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_discovery_default_project_groups(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'project_groups': {
            'include': ['hello'],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-1', 'project_group_name:Default Project Group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-2', 'project_group_name:test-group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-3', 'project_group_name:hello', 'space_id:Spaces-1'],
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_discovery_space_project_groups(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'spaces': {
            'include': [
                {
                    'Default': {
                        'project_groups': {
                            'include': ['hello'],
                        }
                    }
                }
            ],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-1', 'project_group_name:Default Project Group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-2', 'project_group_name:test-group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-3', 'project_group_name:hello', 'space_id:Spaces-1'],
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_discovery_default_projects(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'projects': {
            'include': ['test-api'],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project.count',
        1,
        tags=[
            'project_id:Projects-1',
            'project_name:test-api',
            'project_group_id:ProjectGroups-1',
            'space_id:Spaces-1',
        ],
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        tags=[
            'project_id:Projects-2',
            'project_name:my-project',
            'project_group_id:ProjectGroups-1',
            'space_id:Spaces-1',
        ],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        tags=['project_id:Projects-3', 'project_name:test', 'project_group_id:ProjectGroups-1', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project.count',
        tags=['project_id:Projects-4', 'project_name:hi', 'project_group_id:ProjectGroups-2', 'space_id:Spaces-1'],
        count=0,
    )


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_discovery_space_project_group_projects(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'spaces': {
            'include': [
                {
                    'Default': {
                        'project_groups': {
                            'include': [
                                {
                                    'hello': {
                                        'projects': {
                                            'include': ['.*'],
                                        },
                                    }
                                }
                            ],
                        },
                    }
                }
            ],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])

    get_current_datetime.return_value = MOCKED_TIME1
    dd_run_check(check)

    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-1', 'project_group_name:Default Project Group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        tags=['project_group_id:ProjectGroups-2', 'project_group_name:test-group', 'space_id:Spaces-1'],
        count=0,
    )
    aggregator.assert_metric(
        'octopus_deploy.project_group.count',
        1,
        tags=['project_group_id:ProjectGroups-3', 'project_group_name:hello', 'space_id:Spaces-1'],
    )


@pytest.mark.parametrize(
    ('instance'),
    [
        pytest.param(
            {
                'octopus_endpoint': 'http://localhost:80',
                'spaces': {
                    'include': ['Default'],
                },
                'project_groups': {
                    'include': ['Default Project Group'],
                },
                'projects': {
                    'include': ['.*'],
                },
            },
            id='all default',
        ),
        pytest.param(
            {
                'octopus_endpoint': 'http://localhost:80',
                'spaces': {
                    'include': [
                        {
                            'Default': {
                                'project_groups': {
                                    'include': ['Default Project Group'],
                                },
                            }
                        }
                    ],
                },
                'projects': {
                    'include': ['.*'],
                },
            },
            id='with project groups',
        ),
        pytest.param(
            {
                'octopus_endpoint': 'http://localhost:80',
                'spaces': {
                    'include': [
                        {
                            'Default': {
                                'project_groups': {
                                    'include': [
                                        {
                                            'Default Project Group': {
                                                'projects': {
                                                    'include': ['.*'],
                                                },
                                            }
                                        }
                                    ],
                                },
                            }
                        }
                    ],
                },
            },
            id='with projects',
        ),
    ],
)
@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_run_twice(get_current_datetime, dd_run_check, aggregator, instance):
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count')
    aggregator.assert_metric('octopus_deploy.project_group.count')
    aggregator.assert_metric('octopus_deploy.project.count')

    get_current_datetime.return_value = MOCKED_TIME2
    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count')
    aggregator.assert_metric('octopus_deploy.project_group.count')
    aggregator.assert_metric('octopus_deploy.project.count')


@pytest.mark.usefixtures('mock_http_get')
@mock.patch("datadog_checks.octopus_deploy.check.get_current_datetime")
def test_empty_include(get_current_datetime, dd_run_check, aggregator):
    instance = {
        'octopus_endpoint': 'http://localhost:80',
        'spaces': {
            'include': [],
        },
    }
    check = OctopusDeployCheck('octopus_deploy', {}, [instance])
    get_current_datetime.return_value = MOCKED_TIME1

    dd_run_check(check)

    aggregator.assert_metric('octopus_deploy.space.count', count=0)
