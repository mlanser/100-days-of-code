import configparser
import os
import click

_CSV_    = 'csv'
_JSON_   = 'json'
_SQLite_ = 'sqlite'
_Influx_ = 'influx'



# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
def get_wifi_settings(ctxGlobals):
    ssid = click.prompt("Enter network SSID")
    password = click.prompt("Enter WiFi password")
    security = click.prompt(
        "Enter WiFi security",
        type=click.Choice(['WPA', 'WPA2', 'WEP'], case_sensitive=False),
        default='WPA',
    )
    
    settings = {
        'wifi': {
            'ssid': ssid,
            'security': security.upper(),
            'password': password,
            }
        }

    return settings


def validate_wifi_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('wifi', 'ssid'): 
        return False
    if not settings.has_option('wifi', 'security'): 
        return False
    if not settings.has_option('wifi', 'password'): 
        return False

    return True


def get_data_settings(ctxGlobals):
    dbuser = None
    dbpswd = None

    storage = click.prompt(
        "Enter data storage type", 
        type=click.Choice(['CSV', 'JSON', 'SQLite', 'Influx'], case_sensitive=False)
    )
    if storage.lower() == _CSV_:
        db = click.prompt(
            "Enter path to CSV data file",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'data.csv'),
        )
    elif storage.lower() == _JSON_:
        db = click.prompt(
            "Enter path to JSON data file",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'data.json'),
        )
    elif storage.upper() == _SQLite_:
        db = click.prompt(
            "Enter path to SQLite database. Note: ':memory:' is not supported.",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'data.sqlite'),
        )
    else:
        db = click.prompt("Enter database URI")
        dbuser = click.prompt("Enter database user name", default='')
        dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
    
    settings = {
        'data': {
            'storage': storage,
            'db': db,
            'dbuser': dbuser,
            'dbpswd': dbpswd,
            }
        }
    
    return settings


def validate_data_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('data', 'storage'): 
        return False
    if not settings.has_option('data', 'db'): 
        return False

    return True


def get_speedtest_settings(ctxGlobals):
    uri = click.prompt(
        "Enter URI for 'speedtest-cli'",
        type=click.Path(),
        default=click.get_app_dir('speedtest-cli')
    )
    settings = {
        'speedtest': {
            'URI': uri,
            }
        }
    
    # /usr/local/bin/speedtest-cli
    
    return settings


def validate_speedtest_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('speedtest', 'foo'): 
        return False

    return True


def read_settings(ctxGlobals):
    if os.path.exists(ctxGlobals['configFName']):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(ctxGlobals['configFName'])
    else:
        raise click.ClickException("Config file '{}' does NOT exist or cannot be accessed!".format(ctxGlobals['configFName']))

    return config
        
        
def save_settings(ctxGlobals, section):
    config = configparser.ConfigParser(allow_no_value=True)
    if os.path.exists(ctxGlobals['configFName']):
        config.read(ctxGlobals['configFName'])
    else:
        path = os.path.dirname(os.path.abspath(ctxGlobals['configFName']))
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise click.ClickException("Config file '{}' does NOT exist or cannot be accessed!".format(ctxGlobals['configFName']))
    
    if section == 'wifi':
        config.read_dict(get_wifi_settings(ctxGlobals))
    elif section == 'data':
        config.read_dict(get_data_settings(ctxGlobals))
    elif section == 'speedtest':
        config.read_dict(get_speedtest_settings(ctxGlobals))
    else:
        raise click.BadParameter("Invalid section '{}'".format(section))
    
    with open(ctxGlobals['configFName'], 'w') as configFile:
        config.write(configFile)


def isvalid_settings(settings):
    if not validate_wifi_settings(settings):
        return False
    if not validate_data_settings(settings):
        return False
    #if not validate_speedtest_settings(settings):
    #    return False
    #
    # Need to put in some actual tests here
    #
    return True