# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import datetime
import os

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

DEFAULT_COLLECTION_INTERVAL = 15
MOCKED_TIME1 = datetime.datetime.fromisoformat("2024-09-23T14:45:00.123+00:00")
MOCKED_TIME2 = MOCKED_TIME1 + datetime.timedelta(seconds=DEFAULT_COLLECTION_INTERVAL)

E2E_METRICS = [
    "octopus_deploy.space.count",
    "octopus_deploy.project_group.count",
    "octopus_deploy.project.count",
    "octopus_deploy.deployment.count",
    "octopus_deploy.deployment.queued_time",
    "octopus_deploy.deployment.executing_time",
    "octopus_deploy.server_node.count",
    "octopus_deploy.server_node.in_maintenance_mode",
    "octopus_deploy.server_node.max_concurrent_tasks",
]

ALL_METRICS = ["octopus_deploy.deployment.completed_time"] + E2E_METRICS

ALL_DEPLOYMENT_LOGS = [
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment failed because one or more steps failed. Please see the deployment log for details.',
        'timestamp': 1727104203218,
        'status': 'Fatal',
        'stage_name': 'Deploy test release 0.0.2 to Development',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727104198525,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': "The step failed: Activity Run a Script on the Octopus Server failed with error "
        "'The remote script failed with exit code 1'.",
        'timestamp': 1727104202767,
        'status': 'Fatal',
        'stage_name': 'Step 2: Run a Script',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'ParserError: At /home/octopus/.octopus/OctopusServer/Server/Work/'
        '09234928998123-1847-68/Script.ps1:1 char:6',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+ echo "stop',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+      ~~~~~',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The string is missing the terminator: ".',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'At /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/Script.ps1:1 char:6',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+ echo "stop',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+      ~~~~~',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202606,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/'
        'Octopus.FunctionAppenderContext.ps1: line 258',
        'timestamp': 1727104202606,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/'
        'Bootstrap.Octopus.FunctionAppenderContext.ps1: line 1505',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The remote script failed with exit code 1',
        'timestamp': 1727104202733,
        'status': 'Fatal',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The action Run a Script on the Octopus Server failed',
        'timestamp': 1727104202758,
        'status': 'Fatal',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1846,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment completed successfully.',
        'timestamp': 1727103628255,
        'status': 'Info',
        'stage_name': 'Deploy test release 0.0.1 to Staging',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1846,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727103627639,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1845,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment completed successfully.',
        'timestamp': 1727103621669,
        'status': 'Info',
        'stage_name': 'Deploy test release 0.0.1 to Development',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1845,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727103621208,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test-api,task_id:ServerTasks-1844,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment completed successfully.',
        'timestamp': 1727103442532,
        'status': 'Info',
        'stage_name': 'Deploy test-api release 0.1.5 to Development',
    },
    {
        'ddtags': 'space_name:Default,project_name:test-api,task_id:ServerTasks-1844,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'Testing',
        'timestamp': 1727103440967,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test-api,task_id:ServerTasks-1844,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'test',
        'timestamp': 1727103442029,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
]

ONLY_TEST_LOGS = [
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment failed because one or more steps failed. Please see the deployment log for details.',
        'timestamp': 1727104203218,
        'status': 'Fatal',
        'stage_name': 'Deploy test release 0.0.2 to Development',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727104198525,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': "The step failed: Activity Run a Script on the Octopus Server failed with error "
        "'The remote script failed with exit code 1'.",
        'timestamp': 1727104202767,
        'status': 'Fatal',
        'stage_name': 'Step 2: Run a Script',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'ParserError: At /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/'
        'Script.ps1:1 char:6',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+ echo "stop',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+      ~~~~~',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The string is missing the terminator: ".',
        'timestamp': 1727104202599,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'At /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/Script.ps1:1 char:6',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+ echo "stop',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': '+      ~~~~~',
        'timestamp': 1727104202605,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202606,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/'
        'Octopus.FunctionAppenderContext.ps1: line 258',
        'timestamp': 1727104202606,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, /home/octopus/.octopus/OctopusServer/Server/Work/09234928998123-1847-68/'
        'Bootstrap.Octopus.FunctionAppenderContext.ps1: line 1505',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'at <ScriptBlock>, <No file>: line 1',
        'timestamp': 1727104202607,
        'status': 'Error',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The remote script failed with exit code 1',
        'timestamp': 1727104202733,
        'status': 'Fatal',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1847,'
        'task_name:Deploy,task_state:Failed,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The action Run a Script on the Octopus Server failed',
        'timestamp': 1727104202758,
        'status': 'Fatal',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1846,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment completed successfully.',
        'timestamp': 1727103628255,
        'status': 'Info',
        'stage_name': 'Deploy test release 0.0.1 to Staging',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1846,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727103627639,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1845,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'The deployment completed successfully.',
        'timestamp': 1727103621669,
        'status': 'Info',
        'stage_name': 'Deploy test release 0.0.1 to Development',
    },
    {
        'ddtags': 'space_name:Default,project_name:test,task_id:ServerTasks-1845,'
        'task_name:Deploy,task_state:Success,server_node:OctopusServerNodes-50c3dfbarc82',
        'message': 'hello',
        'timestamp': 1727103621208,
        'status': 'Info',
        'stage_name': 'Octopus Server',
    },
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
