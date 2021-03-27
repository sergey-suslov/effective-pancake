import os
import ssl
import unittest
try:
    from unittest import mock  # pylint: disable-msg=E0611
except ImportError:
    import mock

import cassandra

from cdeploy import exceptions as exc
from cdeploy import migrator
from cdeploy import cqlexecutor


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_MIGRATIONS_PATH = os.path.join(TEST_DIR, './migrations')

migration_1_content = open(
    os.path.join(TEST_MIGRATIONS_PATH, '001_create_users.cql')
).read()
migration_2_content = open(
    os.path.join(TEST_MIGRATIONS_PATH, '002_add_firstname.cql')
).read()


class ApplyingMigrationTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)
        self.migrator.get_top_version = mock.Mock(return_value=0)

    def test_it_should_make_sure_the_schema_migrations_table_exists(self):
        cqlexecutor.CQLExecutor.init_table = mock.Mock()
        self.migrator.run_migrations()
        cqlexecutor.CQLExecutor.init_table.assert_called_once_with(
            self.session
        )

    def test_it_should_initially_apply_all_the_migrations(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.run_migrations()
        cqlexecutor.CQLExecutor.execute.assert_has_calls([
            mock.call(self.session, migration_1_content),
            mock.call(self.session, migration_2_content)
        ])

    def test_it_should_add_migration_versions_to_schema_migrations_table(self):
        cqlexecutor.CQLExecutor.add_schema_migration = mock.Mock()
        self.migrator.run_migrations()

        cqlexecutor.CQLExecutor.add_schema_migration.assert_has_calls([
            mock.call(self.session, 1),
            mock.call(self.session, 2)
        ])

    def test_it_should_only_run_migrations_that_have_not_been_applied(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.get_top_version = mock.Mock(return_value=1)
        self.migrator.run_migrations()

        cqlexecutor.CQLExecutor.execute.assert_called_once_with(
            self.session,
            migration_2_content
        )

    def test_migration_version(self):
        self.assertEqual(
            123,
            self.migrator.migration_version('123.cql')
        )
        self.assertEqual(
            123,
            self.migrator.migration_version('123_xyz.cql')
        )

    def test_duplicate_schema_version_new_version(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.get_top_version = mock.Mock(return_value=1)
        self.migrator.filter_migrations = mock.Mock(
            return_value=['2_second.cql', '2_third.cql'])
        with self.assertRaises(exc.DuplicateSchemaVersionError):
            self.migrator.run_migrations()

    def test_duplicate_schema_version_existing_version(self):
        cqlexecutor.CQLExecutor.execute = mock.Mock()
        self.migrator.get_top_version = mock.Mock(return_value=2)
        self.migrator.filter_migrations = mock.Mock(
            return_value=['1_first.cql', '2_second.cql', '2_third.cql'])
        with self.assertRaises(exc.DuplicateSchemaVersionError):
            self.migrator.run_migrations()


class UndoMigrationTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)
        self.migrator.get_top_version = mock.Mock(return_value=2)

    def test_it_should_rollback_the_schema_version(self):
        cqlexecutor.CQLExecutor.rollback_schema_migration = mock.Mock()
        self.migrator.undo()
        cqlexecutor.CQLExecutor.rollback_schema_migration. \
            assert_called_once_with(self.session)

    def test_it_should_rollback_version_2(self):
        cqlexecutor.CQLExecutor.execute_undo = mock.Mock()
        self.migrator.undo()
        cqlexecutor.CQLExecutor.execute_undo.assert_called_once_with(
            self.session,
            migration_2_content
        )

    def test_it_should_do_nothing_if_at_version_0(self):
        self.migrator.get_top_version = mock.Mock(return_value=0)
        cqlexecutor.CQLExecutor.execute_undo = mock.Mock()
        self.migrator.undo()
        self.assertFalse(cqlexecutor.CQLExecutor.execute_undo.called)


class TopSchemaVersionTests(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()
        self.migrator = migrator.Migrator(TEST_MIGRATIONS_PATH, self.session)

    def test_it_should_return_zero_initially(self):
        cqlexecutor.CQLExecutor.get_top_version = mock.Mock(return_value=[])

        self.assertEquals(0, self.migrator.get_top_version())

    def test_it_should_return_the_highest_version_from_schema_migrations(self):
        cqlexecutor.CQLExecutor.get_top_version = \
            mock.Mock(return_value=[mock.Mock(version=7)])
        version = self.migrator.get_top_version()

        self.assertEquals(version, 7)


class SessionTests(unittest.TestCase):
    def setUp(self):
        cluster_patcher = mock.patch('cdeploy.migrator.Cluster')
        self.mock_cluster = cluster_patcher.start()
        self.addCleanup(cluster_patcher.stop)

        self.config = {
            'hosts': ['cassandra.local'],
            'keyspace': 'test',
        }

        self.session = mock.Mock()
        self.session.set_keyspace.return_value = None

        self.returned_cluster = mock.Mock()
        self.returned_cluster.connect.return_value = self.session
        self.mock_cluster.return_value = self.returned_cluster

    def test_auth_disabled(self):
        migrator.get_cluster(self.config)

        args, kwargs = self.mock_cluster.call_args
        self.assertEqual(None, kwargs['auth_provider'])

    def test_auth_enabled(self):
        self.config['auth_enabled'] = True
        self.config['auth_username'] = 'username'
        self.config['auth_password'] = 'password'

        patch_path = 'cdeploy.migrator.auth.PlainTextAuthProvider'
        with mock.patch(patch_path) as mock_provider:
            provider = mock.Mock()
            mock_provider.return_value = provider

            migrator.get_cluster(self.config)

            args, kwargs = mock_provider.call_args
            self.assertEqual(self.config['auth_username'], kwargs['username'])
            self.assertEqual(self.config['auth_password'], kwargs['password'])

            args, kwargs = self.mock_cluster.call_args
            self.assertEqual(provider, kwargs['auth_provider'])

    def test_ssl_disabled(self):
        migrator.get_cluster(self.config)

        args, kwargs = self.mock_cluster.call_args
        self.assertEqual(None, kwargs['ssl_options'])

    def test_ssl_enabled(self):
        self.config['ssl_enabled'] = True
        self.config['ssl_ca_certs'] = '/path/to/ca/certs'

        migrator.get_cluster(self.config)

        args, kwargs = self.mock_cluster.call_args
        self.assertEqual(
            {
                'ca_certs': self.config['ssl_ca_certs'],
                'ssl_version': ssl.PROTOCOL_TLSv1,  # pylint: disable=E1101
            },
            kwargs['ssl_options'],
        )

    def test_consistency_level_default(self):
        level = mock.Mock()
        mock_session = mock.Mock(default_consistency_level=level)
        mock_cluster = mock.Mock()
        mock_cluster.connect.return_value = mock_session
        self.mock_cluster.return_value = mock_cluster

        session = migrator.configure_session(mock_session, self.config)

        self.assertEqual(level, session.default_consistency_level)

    def test_consistency_level_ALL(self):
        self.config['consistency_level'] = 'ALL'

        session = migrator.configure_session(self.session, self.config)

        self.assertEqual(
            cassandra.ConsistencyLevel.ALL,
            session.default_consistency_level,
        )

    def test_consistency_level_EACH_QUORUM(self):
        self.config['consistency_level'] = 'EACH_QUORUM'

        session = migrator.configure_session(self.session, self.config)

        self.assertEqual(
            cassandra.ConsistencyLevel.EACH_QUORUM,
            session.default_consistency_level,
        )

    def test_nonexistent_keyspace_create_enabled(self):
        self.config['create_keyspace'] = True
        self.config['replication_strategy'] = 'test'

        self.session.set_keyspace.side_effect = [
            cassandra.InvalidRequest,
            None
        ]

        migrator.configure_session(self.session, self.config)
        ((args,), _) = self.session.set_keyspace.call_args
        self.assertEqual(self.config["keyspace"], args)

        ((args,), _) = self.session.execute.call_args
        self.assertEqual(
            "CREATE KEYSPACE {0} WITH REPLICATION = {1};".format(
                self.config["keyspace"],
                self.config["replication_strategy"]
            ),
            args
        )

    def test_nonexistent_keyspace_create_disabled(self):
        self.config['create_keyspace'] = False

        self.session.set_keyspace.side_effect = cassandra.InvalidRequest

        with self.assertRaises(cassandra.InvalidRequest):
            migrator.configure_session(self.session, self.config)

        ((args,), _) = self.session.set_keyspace.call_args
        self.assertEqual(self.config["keyspace"], args)


if __name__ == '__main__':
    unittest.main()
