from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    """
    Service configuration
    """
    DEBUG = True   # For some reason, setting this to True causes JSON to be "pretty-printed"

    # Commented out because these are now retrieved from the helpers.environment.Environment class.
    # PORT = 5010
    # MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Match')
    # # Some instances of the DB are named 'Match' and others 'match'.
    # DB_NAME = 'match' if '/match' in MONGODB_URI else 'Match'
