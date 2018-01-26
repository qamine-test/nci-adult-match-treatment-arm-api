import logging
import os
from pprint import pformat

import yaml


class Environment(object):
    """
    Maintainer of configuration variables that can vary based on environment.  Implemented as a Singleton so
    that the configuration file is only read once.
    """
    REQ_ENV_VARS = ['ENVIRONMENT', 'MONGODB_URI']
    REQ_VARS_MSG = "The following environment variables must be defined in your" + \
                   " environment in order for application to start:" + \
                   " ".join(REQ_ENV_VARS)
    INVALID_GET_MSG_FMT = 'Invalid item {} requested from ' + __name__ + ' object.'
    CONFIG_FILE = "config/environment.yml"
    MISSING_CONFIG_FILE_MSG = "Configuration file {} is required".format(CONFIG_FILE)

    class __EnvImpl:
        """
        Internal implementation of the Environment for initializing Environment.__instance.
        """
        def __init__(self):
            self.logger = logging.getLogger(__name__)
            try:
                # self.environment = os.environ.get('ENVIRONMENT', 'test')  # assign default until this can be set up
                self.environment = os.environ['ENVIRONMENT']
                self.mongodb_uri = os.environ['MONGODB_URI']
                self.db_name = 'match' if '/match' in self.mongodb_uri else 'Match'

            except KeyError as e:
                self.logger.error(Environment.REQ_VARS_MSG)
                self.logger.error(str(e))
                raise e

            self.logger.info("Environment set to: " + self.environment)

            self.load_config_file()
            self.load_overrides_from_env()

        def load_config_file(self):
            """Read configuration variables from the yaml config file."""
            try:
                with open(os.path.abspath(Environment.CONFIG_FILE), 'r') as yaml_file:
                    self._env = yaml.safe_load(yaml_file)
            except FileNotFoundError as e:
                err_msg = Environment.MISSING_CONFIG_FILE_MSG + ": {}".format(str(e))
                self.logger.exception(err_msg)
                raise FileNotFoundError(Environment.MISSING_CONFIG_FILE_MSG).with_traceback(e.__traceback__)

            self.logger.debug("Variables loaded from config file for {env}:\n{vars}"
                             .format(env=self.environment, vars=pformat(self._env[self.environment])))

        def load_overrides_from_env(self):
            """Any variable in the configuration file can be overridden by an environment variable of the same
               name only in all caps.  For example, the environment variable SQS_QUEUE_NAME overrides the config
               file variable sqs_queue_name.
            """
            for var in self._env[self.environment]:
                if var.upper() in os.environ:
                    self._env[self.environment][var] = os.environ[var.upper()]
                    self.logger.info("Environment variable {} overrides default setting for {}; new value='{}'"
                              .format(var.upper(), var, self._env[self.environment][var]))

    # The private instance variable
    __instance = None

    def __init__(self):
        """
        Initializes the __instance if needed.
        """
        if self.__instance is None:
            Environment.__instance = Environment.__EnvImpl()

    def __getattr__(self, item):
        """
        Provides top level read access to the item so that the caller need not know the internal representation.
        :param item:
        :return: the requested item
        """
        if item == 'environment':
            return self.__instance.environment
        elif item == 'mongodb_uri':
            return self.__instance.mongodb_uri
        elif item == 'db_name':
            return self.__instance.db_name
        elif item in self.__instance._env[self.__instance.environment]:
            return self.__instance._env[self.__instance.environment][item]
        else:
            raise Exception(Environment.INVALID_GET_MSG_FMT.format(item))

    @classmethod
    def _drop(cls):
        """
        Not intended for production code.  Only to be used for unit testing to ensure a new instance is created
        for each test case.
        :return:
        """
        cls.__instance = None
