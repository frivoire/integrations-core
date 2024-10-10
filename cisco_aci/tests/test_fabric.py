# (C) Datadog, Inc. 2010-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

from freezegun import freeze_time

from datadog_checks.base.utils.containers import hash_mutable
from datadog_checks.cisco_aci import CiscoACICheck
from datadog_checks.cisco_aci.api import Api

from . import common
from .fixtures.metadata import (
    EXPECTED_INTERFACE_METADATA,
    EXPECTED_METADATA_EVENTS,
)


def test_fabric_mocked(aggregator):
    check = CiscoACICheck(common.CHECK_NAME, {}, [common.CONFIG_WITH_TAGS])
    api = Api(common.ACI_URLS, check.http, common.USERNAME, password=common.PASSWORD, log=check.log)
    api.wrapper_factory = common.FakeFabricSessionWrapper
    check._api_cache[hash_mutable(common.CONFIG_WITH_TAGS)] = api

    node101 = '10.0.200.0'
    node102 = '10.0.200.1'
    node201 = '10.0.200.5'
    node202 = '10.0.200.2'
    hn101 = 'pod-1-node-101'
    hn102 = 'pod-1-node-102'
    hn201 = 'pod-1-node-201'
    hn202 = 'pod-1-node-202'
    device_hn101 = 'leaf101'
    device_hn102 = 'leaf102'
    device_hn201 = 'spine201'
    device_hn202 = 'spine202'
    namespace = 'default'

    device_tags_101 = [
        'device_hostname:{}'.format(device_hn101),
        'device_id:{}:{}'.format(namespace, node101),
        'device_ip:{}'.format(node101),
        'device_namespace:{}'.format(namespace),
        'dd.internal.resource:ndm_device_user_tags:default:10.0.200.0',
    ]
    device_tags_102 = [
        'device_hostname:{}'.format(device_hn102),
        'device_id:{}:{}'.format(namespace, node102),
        'device_ip:{}'.format(node102),
        'device_namespace:{}'.format(namespace),
        'dd.internal.resource:ndm_device_user_tags:default:10.0.200.1',
    ]
    device_tags_201 = [
        'device_hostname:{}'.format(device_hn201),
        'device_id:{}:{}'.format(namespace, node201),
        'device_ip:{}'.format(node201),
        'device_namespace:{}'.format(namespace),
        'dd.internal.resource:ndm_device_user_tags:default:10.0.200.5',
    ]
    device_tags_202 = [
        'device_hostname:{}'.format(device_hn202),
        'device_id:{}:{}'.format(namespace, node202),
        'device_ip:{}'.format(node202),
        'device_namespace:{}'.format(namespace),
        'dd.internal.resource:ndm_device_user_tags:default:10.0.200.2',
    ]

    tags000 = ['cisco', 'project:cisco_aci', 'medium:broadcast', 'snmpTrapSt:enable', 'fabric_pod_id:1']
    tags101 = tags000 + ['node_id:101'] + device_tags_101
    tags102 = tags000 + ['node_id:102'] + device_tags_102
    tags201 = tags000 + ['node_id:201'] + device_tags_201
    tags202 = tags000 + ['node_id:202'] + device_tags_202
    tags = ['fabric_state:active', 'fabric_pod_id:1', 'cisco', 'project:cisco_aci']
    leaf101 = ['switch_role:leaf', 'apic_role:leaf', 'node_id:101']
    leaf102 = ['switch_role:leaf', 'apic_role:leaf', 'node_id:102']
    leaf201 = ['switch_role:spine', 'apic_role:spine', 'node_id:201']
    leaf202 = ['switch_role:spine', 'apic_role:spine', 'node_id:202']
    tagsleaf101 = tags + leaf101 + device_tags_101
    tagsleaf102 = tags + leaf102 + device_tags_102
    tagsspine201 = tags + leaf201 + device_tags_201
    tagsspine202 = tags + leaf202 + device_tags_202

    with freeze_time("2012-01-14 03:21:34"):
        check.check({})

        ndm_metadata = aggregator.get_event_platform_events("network-devices-metadata")
        expected_metadata = [event.model_dump(mode="json", exclude_none=True) for event in EXPECTED_METADATA_EVENTS]
        assert ndm_metadata == expected_metadata

        interface_tag_mapping = {
            'default:10.0.200.0': (device_hn101, hn101),
            'default:10.0.200.1': (device_hn102, hn102),
            'default:10.0.200.5': (device_hn201, hn201),
            'default:10.0.200.2': (device_hn202, hn202),
        }

        for interface in EXPECTED_INTERFACE_METADATA:
            device_hn, hn = interface_tag_mapping.get(interface.device_id)
            device_namespace, device_ip = interface.device_id.split(':')
            interface_tags = [
                'port:{}'.format(interface.name),
                'medium:broadcast',
                'snmpTrapSt:enable',
                'node_id:{}'.format(hn.split('-')[-1]),
                'fabric_pod_id:1',
                'device_ip:{}'.format(device_ip),
                'device_namespace:{}'.format(device_namespace),
                'device_hostname:{}'.format(device_hn),
                'device_id:{}'.format(interface.device_id),
                'port.status:{}'.format(interface.status),
                'dd.internal.resource:ndm_device_user_tags:{}'.format(interface.device_id),
                'dd.internal.resource:ndm_interface_user_tags:{}:{}'.format(interface.device_id, interface.index),
            ]
            aggregator.assert_metric('cisco_aci.fabric.port.status', value=1.0, tags=interface_tags, hostname=device_hn)

    metric_name = 'cisco_aci.fabric.port.ingr_total.bytes.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=348576910448.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=261593756524.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=365920898157.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=184416736.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=538866383200.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2750448272939.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=40951085908.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375501844536591.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=861808554.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=6544736275.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=223494309988.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=213271610129.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=6088216934.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=310112731441.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=282986646729.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=163927500429.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=156170003637.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=484418669518.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=56557060354.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=843153621140.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=659049799003.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=816067993294.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=658681144561.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.cpu.idle.min'
    aggregator.assert_metric(metric_name, value=83.786848, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=92.911296, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=86.315524, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=93.498803, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=85.685484, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=92.499371, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=86.347003, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=93.486493, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=85.575467, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=93.764988, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=85.712484, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=93.505349, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=86.685125, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=93.787802, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=85.80775, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=93.592331, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=86.875946, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=94.04867, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=85.712486, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=93.072061, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=86.072144, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=93.783102, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=85.889029, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=93.796495, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=64.258458, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=62.515851, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=61.886601, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=60.908168, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=63.308805, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=61.950724, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=64.70439, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=62.812022, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=64.88201, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=62.138141, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=65.337735, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=62.392077, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=59.512319, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=68.422392, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=59.588519, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=66.581892, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=59.29878, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=66.844242, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=59.42435, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=71.120142, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=60.621498, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=67.77891, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=60.925973, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=68.634969, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.node.mem.free.min'
    aggregator.assert_metric(metric_name, value=13867492.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13928332.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=5512568.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=5445040.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.flood'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=720.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1436.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=658.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=860.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1318.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.flood.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=94.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=188.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=94.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=128972.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=31161278.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14872.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=50788.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=17912.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3384.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2031662.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=539316624.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=976989777.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=368613954.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=702456503.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=218267390.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=94.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=188.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=38102122.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=39593148.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.health.cur'
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=98.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=99.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.node.cpu.idle.max'
    aggregator.assert_metric(metric_name, value=96.391948, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.448433, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.325758, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.400152, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.387064, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.435343, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.396966, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.382037, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.29256, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.363177, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.432186, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.364095, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=96.663283, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.51295, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.569987, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.614452, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.5012, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.490342, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.445677, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.46286, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.452916, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.611027, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.499874, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=96.529531, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=87.864078, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.677846, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=88.166284, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.827858, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.962012, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.770701, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.831633, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.984694, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.719745, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=88.017374, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=87.965324, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=88.035714, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=88.118307, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=87.630706, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.107417, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.193384, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.364379, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.184365, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.27129, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=87.903431, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.510747, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.244314, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=88.002047, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=87.982613, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.multicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1884382.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=98284267.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3672.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=100145009.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=855.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5652770907.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2224410566.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=3865435435.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=4030471655.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_total.pkts.rate'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.03,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.03,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=360.595,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.014286,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.014286,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3.690476,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=300929.061905,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.02381,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=7275.066667,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.014286,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.047619,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.12381,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.234783,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=480.665217,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=76.082609,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=317.378261,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.05,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.777778,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=314.181481,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=259.740741,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=535.933333,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=480.72963,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.033333,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.018519,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.017857,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3.196429,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.025,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.014286,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.017857,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.014286,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.046429,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=295.413809,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=92.93851,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=246.675923,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=332.215125,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.fault_counter.warn'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/51', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:51'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/52', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:52'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/53', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:53'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/54', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:54'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:34'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:35'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:36'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:37'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:38'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:39'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:40'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:41'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:42'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:43'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:44'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:45'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:46'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:47'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/51', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:51'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/52', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:52'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/53', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:53'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/54', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:54'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:16'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:18'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:13'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:14'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:20'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:19'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:21'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:22'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:23'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:24'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:25'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:26'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:27'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:28'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:29'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:30'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:31'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:32'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:33'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:34'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:35'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:36'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:3'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:4'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:5'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:6'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:7'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:8'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:9'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:10'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:11'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:12'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:13'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:14'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:15'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:16'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:17'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:18'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:19'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:20'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:21'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:22'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:23'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:24'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:25'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:26'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:27'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:28'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:29'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:30'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:31'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:32'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:33'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:34'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:35'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:36'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:3'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:4'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:5'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:6'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:7'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:8'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:9'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:10'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:11'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:12'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:13'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:14'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:15'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:16'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:17'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:18'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:19'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:20'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:21'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:22'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:23'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:24'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:25'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:26'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:27'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:28'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:29'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:30'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:31'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:32'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.cpu.avg'
    aggregator.assert_metric(metric_name, value=5.099699999999999, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.6183149999999955, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.986987999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.5842289999999934, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=5.004906000000005, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.652297000000004, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.986576999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.6488959999999935, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=5.079667000000001, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.514444999999995, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=5.043931999999998, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.568399999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=4.930536000000004, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.497870000000006, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.910968999999994, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.510873000000004, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.940123999999997, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.563612000000006, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.955282999999994, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.540270000000007, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=5.002808999999999, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.462749000000002, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.969452000000004, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=4.465964999999997, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=17.815427, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=19.114099999999993, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=17.931529999999995, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=18.983119000000002, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=17.880464000000003, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=18.782194000000004, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=17.751796999999996, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=19.094292999999993, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=17.698178999999996, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=19.134788999999998, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=17.725645999999998, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=19.067124000000007, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=4.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=10.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=19.234358, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.76097, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=19.010105999999993, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.649265, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=18.986099999999993, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.444975, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=19.101067999999998, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.846044000000006, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=18.921163000000007, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.827544000000003, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=19.068934999999996, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=17.649720000000002, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=8.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.multicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236383592.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236450478.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=547520.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=287182563.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=21312.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=318246201.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=18204.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4488.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236423309.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=446236358.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1466364460.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1133167391.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=445946184.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1195355049.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1558331294.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=236470350.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=236534244.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=549032.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=127544.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=280084025.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=278551439.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=829143147.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=3015349024.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2484948057.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=1005106879.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.multicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236383592.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236450478.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=547520.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=287182563.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=21312.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=318246201.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=18204.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4488.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=236423309.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=446236358.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1466364460.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1133167391.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=445946184.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1195355049.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1558331294.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=236470350.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=236534244.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=549032.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=127544.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=280084025.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=278551439.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=829143147.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=3015349024.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2484948057.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=1005106879.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.cpu.max'
    aggregator.assert_metric(metric_name, value=3.6080520000000007, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.5515670000000057, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.6742420000000067, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.5998479999999944, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.612936000000005, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.564656999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.603033999999994, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.617963000000003, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.7074400000000054, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.636823000000007, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.5678139999999985, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.635904999999994, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=3.336716999999993, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.4870499999999964, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.4300130000000024, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.385548, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.498800000000003, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.5096580000000017, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.5543229999999966, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.5371399999999937, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.547083999999998, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.388972999999993, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.5001259999999945, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=3.4704689999999943, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=12.135921999999994, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.322153999999998, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=11.833715999999995, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.172141999999994, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.037987999999999, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.229298999999997, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.168367000000003, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.015305999999995, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.280254999999997, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=11.982625999999996, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=12.034676000000005, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=11.964286000000001, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=7.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=14.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=11.881692999999999, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=12.369293999999996, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.892583000000002, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.806616000000005, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.635621, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.815635, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.728710000000007, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=12.096569000000002, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.489253000000005, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.755685999999997, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=11.997952999999995, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=12.017387, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=11.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.node.mem.avg'
    aggregator.assert_metric(metric_name, value=10559963.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=10491187.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=10747828.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=37859173.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=43008145.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=10814699.0, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=34463186.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.multicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1884382.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=98284267.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3672.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=100145009.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=855.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5652770907.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2224410566.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=3865435435.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=4030471655.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.unicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=370475792067.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=263131271762.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=342315261222.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=242134018.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=344482735664.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375462007802685.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=72584223945.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2717547044839.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=30785612.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122270987.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=913331247.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1918138777.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=77293415849.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=330426792155.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=302746138922.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=62665015.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=222183688736.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=212143547054.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=134113229564.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=203653209556.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=91067116.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238624.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=7077.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238908.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=10568776.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=531249211611.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=172484213872.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30565216.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780750.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780464.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=689750718034.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=843245090540.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=694427252279.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=808249335135.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.capacity.apic.fabric_node.utilized'
    aggregator.assert_metric(metric_name, value=0.0, tags=['cisco', 'project:cisco_aci'], hostname='')

    metric_name = 'cisco_aci.fabric.port.fault_counter.crit'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/51', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:51'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/52', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:52'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/53', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:53'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/54', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:54'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:34'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:35'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:36'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:37'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:38'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:39'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:40'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:41'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:42'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:43'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:44'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:45'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:46'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:47'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/51', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:51'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/52', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:52'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/53', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:53'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/54', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:54'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:16'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:18'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:13'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:14'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:20'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:19'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:21'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:22'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:23'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:24'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:25'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:26'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:27'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:28'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:29'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:30'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:31'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:32'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:33'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:34'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:35'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:36'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:3'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:4'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:5'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:6'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:7'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:8'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:9'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:10'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:11'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:12'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:13'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:14'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:15'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:16'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:17'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:18'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:19'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:20'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:21'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:22'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:23'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:24'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:25'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:26'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:27'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:28'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:29'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:30'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:31'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:32'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:33'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:34'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:35'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:36'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:3'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:4'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:5'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:6'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:7'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:8'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:9'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:10'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:11'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:12'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:13'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:14'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:15'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:16'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:17'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:18'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:19'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:20'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:21'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:22'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:23'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:24'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:25'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:26'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:27'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:28'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:29'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:30'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:31'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:32'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.mem.free.max'
    aggregator.assert_metric(metric_name, value=13903716.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13975396.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=5531456.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=5480244.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.node.health.min'
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=98.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=99.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.port.egr_drop_pkts.errors'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_total.bytes.rate'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=12.69,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=12.69,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=57725.02,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.057143,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.057143,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=905.104762,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=455461817.719048,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=854.752381,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=536243.27619,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.085714,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=18.252381,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=35.319048,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=294.643478,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=609002.547826,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=17891.591304,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=82382.26087,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=19.111538,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=76.155556,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=43222.107407,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=44725.892593,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=91797.314815,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=127111.525926,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14.1,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5.259259,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5.071429,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=545.053571,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=797.571429,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.057143,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5.107143,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.085714,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=17.746429,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=41358.029538,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=21604.055876,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=42458.313431,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=89949.365917,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_total.pkts.rate'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=363.5,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.154545,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=7641.245455,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.618182,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=310442.886364,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=127.525532,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=280.691304,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=244.494589,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=160.540741,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=89.862963,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=334.822222,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=401.2,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=583.388889,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3.353571,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.571429,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=61.586206,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=306.708934,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=312.642784,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=255.925206,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.unicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=348576910354.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=261593756336.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=365920898063.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=184287764.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=538835221922.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2750448258067.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=40951035120.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375501844518679.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=861805170.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=6542704613.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=222953108982.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=212196336085.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5719602980.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=309410271266.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=282668234330.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=163927500335.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=156170003449.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=484380566541.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=56517467206.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=837500850233.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=656825388437.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=812202557859.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=654650672906.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.mem.min'
    aggregator.assert_metric(metric_name, value=10534296.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=10462616.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=10737028.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=37835708.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=42962460.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=10788240.0, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=34432104.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.node.mem.free.avg'
    aggregator.assert_metric(metric_name, value=13878048.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13946824.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=5520655.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=5453784.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.node.health.max'
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=72.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=98.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=99.0, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.port.egr_bytes.unicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=370475792067.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=263131271762.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=342315261222.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=242134018.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=344482735664.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375462007802685.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=72584223945.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2717547044839.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=30785612.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122270987.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=913331247.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1918138777.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=77293415849.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=330426792155.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=302746138922.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=62665015.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=222183688736.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=212143547054.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=134113229564.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=203653209556.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=91067116.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238624.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=7077.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238908.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=10568776.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=531249211611.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=172484213872.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30565216.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780750.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780464.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=689750718034.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=843245090540.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=694427252279.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=808249335135.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_drop_pkts.buffer.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.cpu.min'
    aggregator.assert_metric(metric_name, value=16.213151999999994, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=7.088704000000007, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13.684476000000004, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=6.501197000000005, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=14.314515999999998, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=7.5006290000000035, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13.652997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=6.513507000000004, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=14.424532999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=6.235011999999998, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=14.287515999999997, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=6.494651000000005, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=13.314875, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=6.212198000000001, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=14.192250000000001, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=6.4076689999999985, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=13.124054000000001, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=5.951329999999999, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=14.287514000000002, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=6.927938999999995, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=13.927856000000006, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=6.2168980000000005, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=14.110971000000006, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=6.203505000000007, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=35.741541999999995, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=37.484149, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=38.113399, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=39.091832, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=36.691195, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=38.049276, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=35.295609999999996, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=37.187978, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=35.117990000000006, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=37.861859, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=34.662265000000005, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=37.607923, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=3.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=10.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=40.487681, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=31.577607999999998, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=40.411481, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=33.418108000000004, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=40.70122, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=33.155758000000006, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=40.57565, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=28.879858, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=39.378502, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=32.221090000000004, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=39.074027, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=31.365031000000002, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=5.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.port.ingr_total.bytes.rate'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=90611.92381,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1434.072727,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=980405.281818,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=426.390909,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=470253298.663636,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=9446.706753,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=38348.052174,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=40133.308116,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=11900.614815,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=19401.951852,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=88043.459259,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=73281.118519,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=101114.177778,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=782.496429,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=364.992857,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=10014.876235,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=42435.540018,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=85132.918634,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=43235.18282,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_total.pkts'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3191.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=40.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1601321.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=58421.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=16.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=5494.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=804.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3117.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=6.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2475.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2224.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=4491.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3611.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=42.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2990.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=900.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2516.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=4159.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.mem.max'
    aggregator.assert_metric(metric_name, value=10570520.0, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=10509680.0, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=10755916.0, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(
        metric_name,
        value=37901052.0,
        tags=[
            'apic_role:controller',
            'node_id:3',
            'fabric_state:unknown',
            'device_hostname:apic3',
            'device_id:default:10.0.200.3',
            'device_ip:10.0.200.3',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.3',
        ],
        hostname='pod-1-node-3',
    )
    aggregator.assert_metric(
        metric_name,
        value=43199760.0,
        tags=[
            'apic_role:controller',
            'node_id:1',
            'fabric_state:unknown',
            'device_hostname:apic1',
            'device_id:default:10.0.200.4',
            'device_ip:10.0.200.4',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.4',
        ],
        hostname='pod-1-node-1',
    )
    aggregator.assert_metric(metric_name, value=10823444.0, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(
        metric_name,
        value=34637280.0,
        tags=[
            'apic_role:controller',
            'node_id:2',
            'fabric_state:unknown',
            'device_hostname:apic2',
            'device_id:default:10.0.200.6',
            'device_ip:10.0.200.6',
            'device_namespace:default',
            'fabric_pod_id:1',
            'cisco',
            'project:cisco_aci',
            'dd.internal.resource:ndm_device_user_tags:default:10.0.200.6',
        ],
        hostname='pod-1-node-2',
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.flood'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_drop_pkts.buffer'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.flood.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3196.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3196.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1632.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3069384.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=5334816.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=8725392.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3067140.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=826.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5323724.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2992.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2992.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1428.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.unicast.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=348576910354.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=261593756336.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=365920898063.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=184287764.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=538835221922.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2750448258067.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=40951035120.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375501844518679.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=861805170.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=6542704613.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=222953108982.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=212196336085.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=5719602980.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=309410271266.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=282668234330.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=163927500335.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=156170003449.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=484380566541.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=56517467206.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=837500850233.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=656825388437.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=812202557859.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=654650672906.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_total.bytes.cum'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=370712178855.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=263367725436.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=342315810374.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238340.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=242134018.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=344769918227.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2375462007823997.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=72902470146.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2717547063043.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=30785612.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122270987.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4488.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1149754556.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1918138777.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=77742721591.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=331898491431.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=303888031705.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=511678339.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=223379044611.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=213707202072.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=134349702906.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=203889746792.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=91617576.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238624.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=7077.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=14238908.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=10696320.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=531529295636.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=172762765311.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30565216.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780750.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=30780464.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=122246714.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=690579861181.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=846260439564.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=696912200336.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=809254442014.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.node.cpu.idle.avg'
    aggregator.assert_metric(metric_name, value=94.9003, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.381685, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.013012, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.415771, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=94.995094, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.347703, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.013423, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.351104, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=94.920333, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.485555, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=94.956068, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.4316, tags=tagsleaf101, hostname=hn101)
    aggregator.assert_metric(metric_name, value=95.069464, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.50213, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.089031, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.489127, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.059876, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.436388, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.044717, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.45973, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=94.997191, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.537251, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.030548, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=95.534035, tags=tagsleaf102, hostname=hn102)
    aggregator.assert_metric(metric_name, value=82.184573, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=80.8859, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=82.06847, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=81.016881, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=82.119536, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=81.217806, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=82.248203, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=80.905707, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=82.301821, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=80.865211, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=82.274354, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=80.932876, tags=tagsspine202, hostname=hn202)
    aggregator.assert_metric(metric_name, value=80.765642, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.23903, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=80.989894, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.350735, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=81.0139, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.555025, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=80.898932, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.153956, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=81.078837, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.172456, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=80.931065, tags=tagsspine201, hostname=hn201)
    aggregator.assert_metric(metric_name, value=82.35028, tags=tagsspine201, hostname=hn201)

    metric_name = 'cisco_aci.fabric.port.ingr_total.pkts'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3393.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=32.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=99534.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=5117425.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1076.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3046.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2657.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1306.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=978.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=2400.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3240.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=4750.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=33.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=9.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=594.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=3043.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=4105.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=2440.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.multicast'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1942.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=1861.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=2104.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=3024.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.ingr_bytes.unicast'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=631473.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4416.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=12005285.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=383.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=7778795911.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=79624.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=481448.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=433572.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=96126.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=241147.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=453923.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=572700.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=830768.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3720.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=117645.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=393777.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=1633496.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=368236.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.unicast'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=511910.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=8533.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2398311184.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4593.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=4279557.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=425.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=3692.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=7009700.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=189526.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=826893.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=425.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=347116.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=396212.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=758598.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=770134.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=423.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=3842.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=406856.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=260037.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=405394.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=1661743.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    metric_name = 'cisco_aci.fabric.port.egr_bytes.multicast'
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/43', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:43'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/44', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:44'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/45', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:45'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/46', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:46'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/47', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:47'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=744.0,
        tags=tags101 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:48'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=2004.0,
        tags=tags101 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:49'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=1432.0,
        tags=tags101 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:50'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:1'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:2'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:3'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:4'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:5'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:6'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:7'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:8'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:9'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:10'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:11'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:12'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/13', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:13'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/14', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:14'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:15'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/16', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:16'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:17'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/18', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:18'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/19', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:19'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/20', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:20'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/21', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:21'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/22', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:22'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/23', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:23'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/24', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:24'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/25', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:25'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/26', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:26'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/27', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:27'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/28', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:28'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/29', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:29'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/30', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:30'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/31', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:31'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/32', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:32'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:33'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/34', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:34'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/35', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:35'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/36', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:36'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/37', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:37'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/38', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:38'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/39', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:39'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/40', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:40'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/41', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:41'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags101 + ['port:eth101/1/42', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.0:42'],
        hostname=hn101,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/33', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:33'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=560.0,
        tags=tags102 + ['port:eth1/48', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:48'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=864.0,
        tags=tags102 + ['port:eth1/49', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:49'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1580.0,
        tags=tags102 + ['port:eth1/50', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:50'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:1'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:2'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/3', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:3'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/4', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:4'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/15', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:15'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/17', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:17'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/5', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:5'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/6', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:6'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1318.0,
        tags=tags102 + ['port:eth1/7', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:7'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/8', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:8'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/9', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:9'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/10', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:10'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/11', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:11'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=0.0,
        tags=tags102 + ['port:eth1/12', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.1:12'],
        hostname=hn102,
    )
    aggregator.assert_metric(
        metric_name,
        value=1006.0,
        tags=tags202 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:1'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=896.0,
        tags=tags202 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.2:2'],
        hostname=hn202,
    )
    aggregator.assert_metric(
        metric_name,
        value=1196.0,
        tags=tags201 + ['port:eth1/1', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:1'],
        hostname=hn201,
    )
    aggregator.assert_metric(
        metric_name,
        value=620.0,
        tags=tags201 + ['port:eth1/2', 'dd.internal.resource:ndm_interface_user_tags:default:10.0.200.5:2'],
        hostname=hn201,
    )

    aggregator.assert_metric(
        'datadog.cisco_aci.check_interval', metric_type=aggregator.MONOTONIC_COUNT, count=1, tags=['cisco']
    )
    aggregator.assert_metric('datadog.cisco_aci.check_duration', metric_type=aggregator.GAUGE, count=1, tags=['cisco'])
    # Assert coverage for this check on this instance
    aggregator.assert_all_metrics_covered()
