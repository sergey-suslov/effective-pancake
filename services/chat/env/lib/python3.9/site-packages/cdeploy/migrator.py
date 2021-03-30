from __future__ import print_function
import os
import ssl
import sys

import cassandra
from cassandra import auth
from cassandra.cluster import Cluster
import yaml

from cdeploy import cqlexecutor
from cdeploy import exceptions as exc


class Migrator(object):
    def __init__(self, migrations_path, session):
        print('Reading migrations from {0}'.format(migrations_path))
        self.migrations_path = migrations_path
        self.session = session

    def run_migrations(self):
        cqlexecutor.CQLExecutor.init_table(self.session)

        top_version = self.get_top_version()

        def all_migration_filter(f):
            return (
                os.path.isfile(os.path.join(self.migrations_path, f))
            )

        all_migrations = self.filter_migrations(all_migration_filter)
        versions = [self.migration_version(file_name)
                    for file_name in all_migrations]
        duplicates = Migrator._find_duplicates(versions)

        if duplicates:
            raise exc.DuplicateSchemaVersionError(
                "Duplicate schema version(s) : {0}".format(duplicates))

        def new_migration_filter(f):
            return (
                os.path.isfile(os.path.join(self.migrations_path, f)) and
                self.migration_version(f) > top_version
            )

        new_migrations = self.filter_migrations(new_migration_filter)
        [self.apply_migration(file_name) for file_name in new_migrations]

    @staticmethod
    def _find_duplicates(versions):
        duplicates = []
        unique = []
        for version in versions:
            if version not in unique:
                unique.append(version)
            else:
                duplicates.append(version)
        return duplicates

    def undo(self):
        top_version = self.get_top_version()
        if top_version == 0:
            return

        def top_version_filter(f):
            return (
                os.path.isfile(os.path.join(self.migrations_path, f)) and
                self.migration_version(f) == top_version
            )
        top_migration = list(self.filter_migrations(top_version_filter))[0]

        cqlexecutor.CQLExecutor.execute_undo(
            self.session,
            self.read_migration(top_migration)
        )
        cqlexecutor.CQLExecutor.rollback_schema_migration(self.session)
        print('  -> Migration {0} undone ({1})\n'.format(top_version,
                                                         top_migration))

    def get_top_version(self):
        result = cqlexecutor.CQLExecutor.get_top_version(self.session)
        top_version = result[0].version if len(result) > 0 else 0
        print('Current version is {0}'.format(top_version))
        return top_version

    def filter_migrations(self, filter_func):
        dir_list = os.listdir(self.migrations_path)
        if 'config' in dir_list:
            dir_list.remove('config')
        migration_dir_listing = sorted(dir_list, key=self.migration_version)
        return filter(
            filter_func,
            migration_dir_listing)

    def migration_version(self, file_name):
        return int(file_name.split('.')[0].split('_')[0])

    def apply_migration(self, file_name):
        migration_script = self.read_migration(file_name)
        version = self.migration_version(file_name)

        cqlexecutor.CQLExecutor.execute(self.session, migration_script)
        cqlexecutor.CQLExecutor.add_schema_migration(self.session, version)
        print('  -> Migration {0} applied ({1})\n'.format(version, file_name))

    def read_migration(self, file_name):
        migration_file = open(os.path.join(self.migrations_path, file_name))
        return migration_file.read()


DEFAULT_MIGRATIONS_PATH = './migrations'
CONFIG_FILE_PATH = 'config/cassandra.yml'


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print('Usage: cdeploy [path/to/migrations] [--undo]')
        return

    undo = False
    if '--undo' in sys.argv:
        undo = True
        sys.argv.remove('--undo')

    migrations_path = (
        DEFAULT_MIGRATIONS_PATH if len(sys.argv) == 1 else sys.argv[1]
    )

    if (invalid_migrations_dir(migrations_path) or
            missing_config(migrations_path)):
        sys.exit(1)

    config = load_config(migrations_path, os.getenv('ENV'))
    cluster = get_cluster(config)
    session = cluster.connect()
    session = configure_session(session, config)
    migrator = Migrator(migrations_path, session)

    if undo:
        migrator.undo()
    else:
        migrator.run_migrations()
    cluster.shutdown()


def get_cluster(config):
    auth_provider = None
    if 'auth_enabled' in config and config['auth_enabled']:
        auth_provider = auth.PlainTextAuthProvider(
            username=config['auth_username'],
            password=config['auth_password'],
        )

    ssl_options = None
    if 'ssl_enabled' in config and config['ssl_enabled']:
        ssl_options = {
            'ca_certs': config['ssl_ca_certs'],
            'ssl_version': ssl.PROTOCOL_TLSv1,  # pylint: disable=E1101
        }
    port = '9042'
    if 'port' in config:
        port = config['port']

    cluster = Cluster(
        config['hosts'],
        auth_provider=auth_provider,
        port=port,
        ssl_options=ssl_options,
    )
    return cluster


def configure_session(session, config):
    # Set session options.  One dict mapping cdeploy option names to
    # corresponding cassandra session option names; another dict defining any
    # conversions that need to be done on the value in the config file. This
    # way new options can be supported just by adding an entry to each dict.

    optmap = {'consistency_level': 'default_consistency_level',
              'timeout':           'default_timeout'}

    conlevel = cassandra.ConsistencyLevel.name_to_value  # Convenience alias.
    converters = {'default_consistency_level': (lambda s: conlevel[s])}

    sessionopts = {optmap[arg]: config[arg]
                   for arg in optmap.keys()
                   if arg in config}

    for opt, value in sessionopts.items():
        if opt in converters:
            value = converters[opt](value)
        setattr(session, opt, value)

    try:
        session.set_keyspace(config['keyspace'])
    except cassandra.InvalidRequest:
        # Keyspace doesn't exist yet
        if 'create_keyspace' in config and config['create_keyspace']:
            create_keyspace(config, session)
        else:
            raise

    return session


def create_keyspace(config, session):
    session.execute(
        "CREATE KEYSPACE {0} WITH REPLICATION = {1};".format(
                config['keyspace'],
                config['replication_strategy']
        )
    )
    session.set_keyspace(config['keyspace'])


def invalid_migrations_dir(migrations_path):
    if not os.path.isdir(migrations_path):
        print('"{0}" is not a directory'.format(migrations_path))
        return True
    else:
        return False


def missing_config(migrations_path):
    config_path = config_file_path(migrations_path)
    if not os.path.exists(os.path.join(config_path)):
        print('Missing configuration file "{0}"'.format(config_path))
        return True
    else:
        return False


def config_file_path(migrations_path):
    return os.path.join(migrations_path, CONFIG_FILE_PATH)


def load_config(migrations_path, env):
    config_file = open(config_file_path(migrations_path))
    config = yaml.load(config_file)
    return config[env or 'development']


if __name__ == '__main__':
    main()
