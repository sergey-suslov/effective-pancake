import unittest
import os
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra.local'])
session = cluster.connect()


def drop_keyspace(keyspace):
    session.execute('DROP KEYSPACE IF EXISTS {0}'.format(keyspace))


def create_keyspace(keyspace, replication_strategy):
    session.execute(
        "CREATE KEYSPACE {0} WITH REPLICATION = {1};".format(
            keyspace,
            replication_strategy
        )
    )


def reset_db(keyspace):
    drop_keyspace(keyspace)
    create_keyspace(
        keyspace,
        "{'class': 'SimpleStrategy', 'replication_factor': '1'}"
    )


def run_migrator(arg=''):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    result = os.system(
        'cd {0}/..; python migrator.py test/migrations {1}'.format(test_dir,
                                                                   arg)
    )
    return result


def do_undo():
    run_migrator('--undo')


class FirstRunTest(unittest.TestCase):
    def setUp(self):
        os.unsetenv('ENV')
        reset_db('migrations_development')

    def test_migrations_applied(self):
        run_migrator()
        result = session.execute(
            'SELECT * FROM migrations_development.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 2)

    def test_keyspace_nonexistent(self):
        os.putenv('ENV', 'keyspace')
        run_migrator()
        result = session.execute(
            'SELECT * FROM migrations_keyspace_test.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 2)
        drop_keyspace('migrations_keyspace_test')


class UndoTest(unittest.TestCase):
    def setUp(self):
        os.unsetenv('ENV')
        reset_db('migrations_development')

    def test_undo(self):
        run_migrator()
        do_undo()
        result = session.execute(
            'SELECT * FROM migrations_development.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 1)


class DatabaseEnvironmentsTest(unittest.TestCase):
    def setUp(self):
        reset_db('migrations_test')

    def tearDown(self):
        os.unsetenv('ENV')

    def test_changing_env(self):
        os.putenv('ENV', 'test')
        run_migrator()
        result = session.execute(
            'SELECT * FROM migrations_test.schema_migrations LIMIT 1'
        )
        self.assertEquals(result[0].version, 2)


class PortConfigTest(unittest.TestCase):
    def setUp(self):
        reset_db('port_test')

    def tearDown(self):
        os.unsetenv('ENV')

    def test_port_configured(self):
        os.putenv('ENV', 'port')
        result = run_migrator()
        self.assertEquals(result, 0)


if __name__ == '__main__':
    unittest.main()
