import os

from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    """
    Service configuration
    """
    DEBUG = True
    PORT = 5010
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Match')
    # Some instances of the DB are named 'Match' and others 'match'.
    DB_NAME = 'match' if '/match' in MONGODB_URI else 'Match'
