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
#                  Manage WiFi Settings
# ---------------------------------------------------------
def _get_wifi_settings(ctxGlobals):
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


def _validate_wifi_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('wifi', 'ssid'): 
        return False
    if not settings.has_option('wifi', 'security'): 
        return False
    if not settings.has_option('wifi', 'password'): 
        return False

    return True


# ---------------------------------------------------------
#                  Manage Data Settings
# ---------------------------------------------------------
def _get_data_settings(ctxGlobals):
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
    elif storage.lower() == _SQLite_:
        db = click.prompt(
            "Enter path to SQLite database.\nNote: ':memory:' is not supported.",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'data.sqlite'),
        )
    elif storage.lower() == _Influx_:
        db = click.prompt("Enter Influx database URI")
        dbuser = click.prompt("Enter database user name", default='')
        dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
    else:
        raise ValueError("Invalid storage type '{}'".format(storage))
        
    settings = {
        'data': {
            'storage': storage,
            'db': db,
            'dbuser': dbuser,
            'dbpswd': dbpswd,
            }
        }
    
    return settings


def _validate_data_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('data', 'storage'): 
        return False
    if not settings.has_option('data', 'db'): 
        return False

    return True


# ---------------------------------------------------------
#                Manage Misc Test Settings
# ---------------------------------------------------------
def _get_speedtest_settings(ctxGlobals):
    uri = click.prompt(
        "Enter URI for 'speedtest-cli'",
        type=click.Path(),
        default=click.get_app_dir('speedtest-cli')
    )
    params = None
    settings = {
        'speedtest': {
            'URI': uri,
            'params': params
            }
        }
    
    # /usr/local/bin/speedtest-cli
    
    return settings


def _validate_speedtest_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('speedtest', 'uri'):
        return False

    return True


def _get_ntwktest_settings(ctxGlobals):
    uri = click.prompt(
        "Enter URI for 'ntwktest-cli'",
        type=click.Path(),
        default=click.get_app_dir('ntwktest-cli')
    )
    params = None
    settings = {
        'ntwktest': {
            'URI': uri,
            'params': params
            }
        }
    
    # /usr/local/bin/????
    
    return settings


def _validate_ntwktest_settings(settings):
    # @TODO: Need to add actual data validation logic here
    #if not settings.has_option('ntwktest', 'uri'):
    #    return False

    return True


# ---------------------------------------------------------
#                  Manage Data Settings
# ---------------------------------------------------------
def isvalid_settings(settings):
    """Validate (to some degree) that application settings (e.g. ensure that
    that required options are present, etc.).
    
    Args:
        settings: Settings to validate
        
    Returns:
        TRUE if settings pass all tests, else FALSE.
    """
    #
    # Need to put in some actual tests here
    #

    if not _validate_wifi_settings(settings):
        return False

    if not _validate_data_settings(settings):
        return False

    if not _validate_speedtest_settings(settings):
        return False
    
    if not _validate_ntwktest_settings(settings):
        return False

    return True


def read_settings(ctxGlobals):
    """Read/parse all application settings from config file.
    
    Args:
        ctxGlobals: List of misc global values stored in CTX app object
        
    Returns:
        Config object with all settings
        
    Raises:
        OSError:    If unable to read config file 
    """
    if os.path.exists(ctxGlobals['configFName']):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(ctxGlobals['configFName'])
    else:
        raise OSError("Config file '{}' does NOT exist or cannot be accessed!".format(ctxGlobals['configFName']))

    return config
        
        
def save_settings(ctxGlobals, section):
    """Save application settings to config file.
    
    Args:
        ctxGlobals: List of misc global values stored in CTX app object
        section:    Name of section to update. Or use 'all' to update all settings.
        
    Raises:
        ValueError: If invalid section name.
        OSError:    If unable to read config file 
    """
    if not section.lower() in ['wifi', 'data', 'test', 'all']:
        raise ValueError("Invalid section '{}'".format(section))

    config = configparser.ConfigParser(allow_no_value=True)
    if os.path.exists(ctxGlobals['configFName']):
        config.read(ctxGlobals['configFName'])
    else:
        path = os.path.dirname(os.path.abspath(ctxGlobals['configFName']))
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise OSError("Config file '{}' does NOT exist or cannot be accessed!".format(ctxGlobals['configFName']))
    
    if section in ['all', 'wifi']:
        config.read_dict(_get_wifi_settings(ctxGlobals))

    if section in ['all', 'data']:
        config.read_dict(_get_data_settings(ctxGlobals))

    if section in ['all', 'test']:
        config.read_dict(_get_speedtest_settings(ctxGlobals))
        config.read_dict(_get_ntwktest_settings(ctxGlobals))

    with open(ctxGlobals['configFName'], 'w') as configFile:
        config.write(configFile)


def show_settings(ctxGlobals, section):
    """Retrieve and display application settings from config file.
    
    Args:
        ctxGlobals: List of misc global values stored in CTX app object
        section:    Name of section to display. Or use 'all' to view all settings.
        
    Raises:
        ValueError: If invalid section name.
        OSError:    If unable to read config file 
    """

    def _get_option_val(_settings, _section, _option=None):
        outStr = '- n/a -'

        if _section is not None and _option is not None:
            if _settings.has_option(_section, _option):
                outStr = str(_settings[_section][_option])

        return outStr

    if not section.lower() in ['wifi', 'data', 'test', 'all']:
        raise ValueError("Invalid section '{}'".format(section))
        
    settings = read_settings(ctxGlobals)

    if section in ['all', 'wifi']:
        click.echo("\n--- [wifi] --------------------")
        click.echo("SSID:              {}".format(_get_option_val(settings, 'wifi', 'ssid')))
        click.echo("Security:          {}".format(_get_option_val(settings, 'wifi', 'security')))
        click.echo("Password:          {}".format(_get_option_val(settings, 'wifi', 'password')))

    if section in ['all', 'data']:
        click.echo("\n--- [data] --------------------")
        click.echo("Storage:           {}".format(_get_option_val(settings, 'data', 'storage')))
        click.echo("Database (db):     {}".format(_get_option_val(settings, 'data', 'db')))
        click.echo("DB User  (dbuser:  {}".format(_get_option_val(settings, 'data', 'dbuser')))
        click.echo("DB Pswd  (dbpswd): {}".format(_get_option_val(settings, 'data', 'dbpswd')))

    if section in ['all', 'test']:
        click.echo("\n--- [test] --------------------")
        click.echo("SpeedTest CLI URI: {}".format(_get_option_val(settings, 'speedtest', 'uri')))
        click.echo("NtwkTest CLI URI:  {}".format(_get_option_val(settings, 'ntwktest', 'uri')))

    click.echo("\n-------------------------------")
    click.echo("CONFIG: '{}'\n".format(ctxGlobals['configFName']))
