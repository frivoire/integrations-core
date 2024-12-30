# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import re
import time
from urllib.parse import urlparse

import psycopg as pg
from psycopg import ClientCursor
from psycopg.rows import dict_row

from datadog_checks.base import AgentCheck, ConfigurationError, is_affirmative
from datadog_checks.pgbouncer.metrics import (
    CLIENTS_METRICS,
    CONFIG_METRICS,
    DATABASES_METRICS,
    POOLS_METRICS,
    SERVERS_METRICS,
    STATS_METRICS,
)


class ShouldRestartException(Exception):
    pass


class PgBouncer(AgentCheck):
    """Collects metrics from pgbouncer"""

    DB_NAME = 'pgbouncer'
    SERVICE_CHECK_NAME = 'pgbouncer.can_connect'

    def __init__(self, name, init_config, instances):
        super(PgBouncer, self).__init__(name, init_config, instances)
        self.host = self.instance.get('host', '')
        self.port = self.instance.get('port', '')
        self.user = self.instance.get('username', '')
        self.password = self.instance.get('password', '')
        self.tags = self.instance.get('tags', [])
        self.database_url = self.instance.get('database_url')
        self.use_cached = is_affirmative(self.instance.get('use_cached', True))
        self.collect_per_client_metrics = is_affirmative(self.instance.get('collect_per_client_metrics', False))
        self.collect_per_server_metrics = is_affirmative(self.instance.get('collect_per_server_metrics', False))

        if not self.database_url:
            if not self.host:
                raise ConfigurationError("Please specify a PgBouncer host to connect to.")
            if not self.user:
                raise ConfigurationError("Please specify a user to connect to PgBouncer as.")
        self.connection = None

    def _get_service_checks_tags(self):
        host = self.host
        port = self.port
        if self.database_url:
            parsed_url = urlparse(self.database_url)
            host = parsed_url.hostname
            port = parsed_url.port

        service_checks_tags = ["host:%s" % host, "port:%s" % port, "db:%s" % self.DB_NAME]
        service_checks_tags.extend(self.tags)
        service_checks_tags = list(set(service_checks_tags))

        return service_checks_tags

    def _collect_stats(self, db):
        """Query pgbouncer for various metrics"""

        metric_scope = [STATS_METRICS, POOLS_METRICS, DATABASES_METRICS, CONFIG_METRICS]

        if self.collect_per_client_metrics:
            metric_scope.append(CLIENTS_METRICS)
        if self.collect_per_server_metrics:
            metric_scope.append(SERVERS_METRICS)

        try:
            for scope in metric_scope:
                descriptors = scope['descriptors']
                metrics = scope['metrics']
                query = scope['query']

                try:
                    cursor = db.cursor(row_factory=dict_row)
                    self.log.debug("Running query: %s", query)
                    cursor.execute(query)
                    rows = self.iter_rows(cursor)

                except Exception as e:
                    self.log.exception("Not all metrics may be available: %s", str(e))

                else:
                    for row in rows:
                        if 'key' in row:  # We are processing "config metrics"
                            # Make a copy of the row to allow mutation
                            row = row.copy()
                            # We flip/rotate the row: row value becomes the column name
                            row[row['key']] = row['value']
                        # Skip the "pgbouncer" database
                        elif row.get('database') == self.DB_NAME:
                            continue

                        tags = list(self.tags)
                        tags += ["%s:%s" % (tag, row[column]) for (column, tag) in descriptors if column in row]
                        for column, (name, reporter) in metrics:
                            if column in row:
                                value = row[column]
                                if column in ['connect_time', 'request_time']:
                                    self.log.debug("Parsing timestamp; original value: %s", value)
                                    # First get rid of any UTC suffix.
                                    value = re.findall(r'^[^ ]+ [^ ]+', value)[0]
                                    value = time.strptime(value, '%Y-%m-%d %H:%M:%S')
                                    value = time.mktime(value)
                                reporter(self, name, value, tags)

                    if not rows:
                        self.log.warning("No results were found for query: %s", query)

        except pg.Error:
            self.log.exception("Connection error")

            raise ShouldRestartException

    def iter_rows(self, cursor):
        row_num = 0
        rows = iter(cursor)
        while True:
            try:
                row = next(rows)
            except StopIteration:
                break
            except Exception as e:
                self.log.error('Error processing row %d: %s', row_num, e)
            else:
                self.log.debug('Processing row: %r', row)
                yield row

            row_num += 1

    def _get_connect_kwargs(self):
        """
        Get the params to pass to psycopg.connect() based on passed-in vals
        from yaml settings file
        """
        if self.database_url:
            return {'conninfo': self.database_url, 'client_encoding': 'utf-8'}

        if self.host in ('localhost', '127.0.0.1') and self.password == '':
            # Use ident method
            return {'conninfo': "user={} dbname={} client_encoding=utf-8".format(self.user, self.DB_NAME)}

        args = {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'dbname': self.DB_NAME,
            'cursor_factory': ClientCursor,
            'client_encoding': 'utf-8',
        }
        if self.port:
            args['port'] = self.port

        return args

    def _get_connection(self, use_cached=None):
        """Get and memoize connections to instances"""
        use_cached = use_cached if use_cached is not None else self.use_cached
        if self.connection and use_cached:
            return self.connection
        try:
            connect_kwargs = self._get_connect_kwargs()
            connection = pg.connect(**connect_kwargs, autocommit=True)
        except Exception:
            redacted_url = self._get_redacted_dsn()
            message = u'Cannot establish connection to {}'.format(redacted_url)

            self.service_check(
                self.SERVICE_CHECK_NAME, AgentCheck.CRITICAL, tags=self._get_service_checks_tags(), message=message
            )
            raise

        self.connection = connection
        return connection

    def _close_connection(self):
        self.connection.close()
        self.connection = None

    def _get_redacted_dsn(self):
        if not self.database_url:
            return u'pgbouncer://%s:******@%s:%s/%s' % (self.user, self.host, self.port, self.DB_NAME)

        parsed_url = urlparse(self.database_url)
        if parsed_url.password:
            return self.database_url.replace(parsed_url.password, '******')
        return self.database_url

    def check(self, instance):
        try:
            db = self._get_connection()
            self._collect_stats(db)
        except ShouldRestartException:
            self.log.info("Resetting the connection")
            db = self._get_connection(use_cached=False)
            self._collect_stats(db)

        self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.OK, tags=self._get_service_checks_tags())
        self._set_metadata()
        # Avoid holding an open connection
        self._close_connection()

    def _set_metadata(self):
        if self.is_metadata_collection_enabled():
            pgbouncer_version = self.get_version()
            if pgbouncer_version:
                self.set_metadata('version', pgbouncer_version)

    def get_version(self):
        db = self._get_connection()
        version = pg.pq.version_pretty(db.connection.info.server_version)
        return version
