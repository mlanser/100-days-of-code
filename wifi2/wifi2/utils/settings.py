import configparser

sample_config = """
[test]
v1 = one
v2 = 2
v3
"""

def read_settings(configFName):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(sample_config)
    return config


def write_settings(configFName, settings = None):
    config = configparser.ConfigParser(allow_no_value=True)
    pass


