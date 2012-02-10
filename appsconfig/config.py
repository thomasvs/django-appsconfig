# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
Configuration management for separate django environments.

Store the config package in the root of your Django tree.

Create a conf/ directory in the root of your Django tree.

Default values can be stored in conf/default and will be loaded first.

Create different environments as subdirectories of conf/

By default, the environment used will be 'local'.

You can load a different environment by running:

ENV=production python manage.py runserver

Variables that can be used in the configuration files:

 - environment: the directory of the environment being loaded
"""

import os
import sys
import glob
import ConfigParser

class ExpandingConfigParser(ConfigParser.SafeConfigParser):
    """
    I override get so our default variables are used and callers
    don't need to provide them.
    """
    def __init__(self, defaults=None):
        self.vars = {}
        ConfigParser.SafeConfigParser.__init__(self, defaults)

    def get(self, section, option, raw=False):
        return ConfigParser.SafeConfigParser.get(self, section, option, raw,
            self.vars)

class Loader(object):

    """
    I load configuration files from environment directories.
    """

    def __init__(self):

        self._confdir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'conf'))

    def _environment_dir(self, environment):
        return os.path.join(self._confdir, environment)

    def _conf_dir_exists(self, directory):
        return os.path.exists(os.path.join(self._confdir, directory))

    def load(self, environment):
        """
        Load the configuration for the given environment.

        @type  environment: C{str}
        """

        config = ExpandingConfigParser({'id': environment})
        config.vars = {
            'environment': self._environment_dir(environment),
        }

        try:
            self._load_one(config, 'default')
        except KeyError:
            self.log("No default configuration found.")
        self._load_one(config, environment)

        return config

    def settings(self, environment):
        path = os.path.join(self._environment_dir(environment), 'settings.py')
        if os.path.exists(path):
            self.log("Adding settings from %s", path)
            return path
        else:
            self.log("No environment settings.py")
            return None

    def _load_one(self, config, environment):


        path = self._environment_dir(environment)

        if not os.path.exists(path):
            raise KeyError(environment)

        self.log('Loading environment %s', environment)

        for path in glob.glob(os.path.join(path, '*.conf')):
            self.log('Loading configuration file %s', path)
            config.read(path)

    def log(self, message, *args):
        if args:
            print >> sys.stderr, message % args
        else:
            print >> sys.stderr, message

def get_environment():
    return os.environ.get('ENV', 'local')

def settings(environment=None):
    """
    Return the settings file to be loaded additionally for the configured
    environment.

    You can call execfile() from settings.py on the return value if it is
    not None.
    """
    if not environment:
        environment = get_environment()
    loader = Loader()
    return loader.settings(environment)

def load(environment=None):
    """
    Load settings files to be loaded additionally for the configured
    environment.

    @rtype: L{ExpandingConfigParser}
    """
    if not environment:
        environment = get_environment()

    loader = Loader()
    return loader.load(environment)

if __name__ == '__main__':

    config = load()

    print "Your config has the following sections: %s" % ", ".join(
        config.sections())
