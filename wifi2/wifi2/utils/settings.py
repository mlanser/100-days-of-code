import configparser
import os
import click


def get_wifi_settings():
    ssid = click.prompt("Enter network SSID")
    security = click.prompt("Enter WiFi security", type=click.Choice(['WAP', 'WEP'], case_sensitive=False))
    password = click.prompt("Enter WiFi password")
    
    settings = {
        'wifi': {
            'ssid': ssid,
            'security': security.upper(),
            'password': password,
            }
        }

    return settings


def validate_wifi_settings(settings):
    if not settings.has_option('wifi', 'ssid'): 
        return False
    if not settings.has_option('wifi', 'security'): 
        return False
    if not settings.has_option('wifi', 'password'): 
        return False

    return True


def get_data_settings():
    storage = click.prompt("Enter data storage type", type=click.Choice(['JSON', 'SQL', 'Influx'], case_sensitive=False))
    if storage.upper() == 'JSON':
        db = click.prompt("Enter path to JSON data file")
        dbuser = None
        dbpswd = None
    else:
        db = click.prompt("Enter database URI")
        dbuser = click.prompt("Enter database user name", default='')
        dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
    
    settings = {
        'data': {
            'storage': storage,
            'db': db,
            'dbuser': dbuser,
            'dbpsswd': dbpswd,
            }
        }
    
    return settings


def validate_data_settings(settings):
    if not settings.has_option('data', 'storage'): 
        return False
    if not settings.has_option('data', 'db'): 
        return False

    return True


def get_speedtest_settings():
    uri = click.prompt("Enter URI for 'speedtest-cli'")
    settings = {
        'speedtest': {
            'URI': foo,
            }
        }
    
    # /usr/local/bin/speedtest-cli
    
    return settings


def validate_speedtest_settings(settings):
    if not settings.has_option('speedtest', 'foo'): 
        return False

    return True


def read_settings(configFName):
    if os.path.exists(configFName):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(configFName)
    else:
        raise click.ClickException("Config file '{}' does NOT exist or cannot be accessed!".format(configFName))

    return config
        
        
def save_settings(configFName, section):
    config = configparser.ConfigParser(allow_no_value=True)
    if os.path.exists(configFName):
        config.read(configFName)
    
    if section == 'wifi':
        config.read_dict(get_wifi_settings())
    elif section == 'data':
        config.read_dict(get_data_settings())
    elif section == 'speedtest':
        config.read_dict(get_speedtest_settings())
    else:
        raise click.BadParameter("Invalid section '{}'".format(section))
    
    with open(configFName, 'w') as configFile:
        config.write(configFile)


def isvalid_settings(settings):
    if not validate_wifi_settings(settings):
        return False
    #if not validate_data_settings(settings):
    #    return False
    #if not validate_speedtest_settings(settings):
    #    return False
    #
    # Need to put in some actual tests here
    #
    return True