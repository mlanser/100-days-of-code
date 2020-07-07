import os
import click
from configparser import ConfigParser, ExtendedInterpolation

_CSV_    = 'csv'
_JSON_   = 'json'
_SQLite_ = 'sqlite'
_Influx_ = 'influx'


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
#                  Manage WiFi Settings
# ---------------------------------------------------------
#
# [wifi]
# ssid = <some SSID>
# security = WPA|WPA2|WEP
# password = <some wifi password>
#
def _get_wifi_settings(ctxGlobals):
    ssid = click.prompt("Enter network SSID")
    security = click.prompt(
        "Enter WiFi security",
        type=click.Choice(['WPA', 'WPA2', 'WEP'], case_sensitive=False),
        default='WPA',
    )
    password = click.prompt("Enter WiFi password")
    settings = {
        'wifi': {
            'ssid': ssid,
            'security': security.upper(),
            'password': password,
            }
        }

    return settings


def _validate_wifi_settings(settings):
    #
    # We can only verify taht values are stored in 
    # config, but not that the values are correct.
    #
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
#
# [data]
# datadir = <common folder for data files>  - e.g. ~/wifi2/data
# count = [1-100]                           - num rec's to retrieve
# sort = [first|last]                       - retrieve first or last 'count' items
#
def _get_data_settings(ctxGlobals):
    datadir = click.prompt(
        "Enter path to common/default data folder",
        type=click.Path(),
        default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'data'),
    )
    count = click.prompt(
        "Enter default for number of data records to retrieve:",
        type=click.IntRange(APP_MIN_RUNS, APP_MAX_RUNS, clamp=True),
        default=APP_MIN_RUNS,
        show_default=True,
    )
    sort = click.prompt(
        "Select default history list/sort order", 
        type=click.Choice(['first', 'last'], case_sensitive=False)
        default='first',
    )
    settings = {
        'data': {
            'datadir': datadir,
            'count': count,
            'sort': sort.lower(),
            }
        }
    
    return settings


def _validate_data_settings(settings):
    # 
    # There are no required items in this section 
    # and we're only keeping this function to be 
    # consistent with other config sections.
    # 
    return True


# ---------------------------------------------------------
#                Manage SpeedTest Settings
# ---------------------------------------------------------
#
# [<nameof test tool section>]
# uri = <uri/path to test tool>
# params = <any test tool params>
# count = [1-100]                       - num test cycle runs
#
# storage = CSV|JSON|SQLite|Influx      - data storage type
# host = <hostname or file path>        - data storage host. If file-based (i.e. CSV, JSON, SQLite),
#                                         then this is a path/filename)
#   Ex:     ~/speedtest.csv
#           ~/speedtest.json
#           ~/wifi2.sqlite              - SQLite file can hold several tables
#           localhost                   - Influx db server can hold several databases
#
# port = <db server port>               - Used for InfluxDB
# dbuser = <db user w proper access>    - Used for InfluxDB
# dbpswd = <db user password>           - Used for InfluxDB
# dbname = <db name>                    - Used for InfluxDB
# dbtable = <db table name>             - Used for SQLite and Influx
#
def _get_speedtest_settings(ctxGlobals):
    dbport  = None
    dbuser  = None
    dbpswd  = None
    dbname  = None
    dbtable = None

    uri = click.prompt(
        "Enter URI for 'speedtest-cli'",
        type=click.Path(),
        default=click.get_app_dir('speedtest-cli')
    )
    params  = None
    count = click.prompt(
        "Enter default for number of test cycle runs:",
        type=click.IntRange(APP_MIN_RUNS, APP_MAX_RUNS, clamp=True),
        default=APP_MIN_RUNS,
        show_default=True,
    )
    
    storage = click.prompt(
        "Enter data storage type", 
        type=click.Choice(['CSV', 'JSON', 'SQLite', 'Influx'], case_sensitive=False)
    )
    if storage.lower() == _CSV_:
        host = click.prompt(
            "Enter path to CSV data file",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'speedtest.csv'),
        )
    elif storage.lower() == _JSON_:
        host = click.prompt(
            "Enter path to JSON data file",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), 'speedtest.json'),
        )
    elif storage.lower() == _SQLite_:
        host = click.prompt(
            "Enter path to SQLite database.\nNote: ':memory:' is not supported.",
            type=click.Path(),
            default=os.path.join(click.get_app_dir(ctxGlobals['appName']), ctxGlobals['appName'] + '.sqlite'),
        )
        dbTable = click.prompt(
            "Enter name of database table",
            default='SpeedTest'
        )
    elif storage.lower() == _Influx_:
        host = click.prompt("Enter database host name")
        port = click.prompt("Enter database host port", default='')
        dbuser = click.prompt("Enter database user name", default='')
        dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
        dbname = click.prompt(
            "Enter name of database",
            default='SpeedTest'
        )
        dbtable = click.prompt(
            "Enter name of database table",
            default='SpeedTestLog'
        )
    else:
        raise ValueError("Invalid storage type '{}'".format(storage))
        
    settings = {
        'speedtest': {
            'URI': uri,
            'params': params,
            'count': count,
            'host': host,
            'port': port,
            'dbuser': dbuser, # @TODO NEEDS TO BE LOW-LEVEL USER ACCT
            'dbpswd': dbpswd, # @TODO NEED TO ENCRYPT SOMEHOW!!!
            'dbname': dbname,
            'dbtable': dbtable,
            }
        }
    
    # /usr/local/bin/speedtest-cli
    
    return settings


def _validate_speedtest_settings(settings):
    # @TODO: Need to add actual data validation logic here
    if not settings.has_option('speedtest', 'uri'):
        return False

    return True


# ---------------------------------------------------------
#                Manage ????Test Settings
# ---------------------------------------------------------
#
# [<nameof test tool section>]
# uri = <uri/path to test tool>
# params = <any test tool params>
# count = [1-100]                       - num test cycle runs
#
# storage = CSV|JSON|SQLite|Influx      - data storage type
# host = <hostname or file path>        - data storage host. If file-based (i.e. CSV, JSON, SQLite),
#                                         then this is a path/filename)
#   Ex:     ~/speedtest.csv
#           ~/speedtest.json
#           ~/wifi2.sqlite              - SQLite file can hold several tables
#           localhost                   - Influx db server can hold several databases
#
# port = <db server port>               - Used for InfluxDB
# dbuser = <db user w proper access>    - Used for InfluxDB
# dbpswd = <db user password>           - Used for InfluxDB
# dbname = <db name>                    - Used for InfluxDB
# dbtable = <db table name>             - Used for SQLite and Influx
#
def _get_sometest_settings(ctxGlobals):
    uri = click.prompt(
        "Enter URI for 'sometest-cli'",
        type=click.Path(),
        default=click.get_app_dir('sometest-cli')
    )
    params = None
    count = click.prompt(
        "Enter default for number of test cycle runs:",
        type=click.IntRange(APP_MIN_RUNS, APP_MAX_RUNS, clamp=True),
        default=APP_MIN_RUNS,
        show_default=True,
    )
    
    settings = {
        'sometest': {
            'URI': uri,
            'params': params,
            'count': count
            }
        }
    
    # /usr/local/bin/????
    
    return settings


def _validate_sometest_settings(settings):
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
    
    if not _validate_sometest_settings(settings):
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
        config = configparser.ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
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

    config = configparser.ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
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
        config.read_dict(_get_sometest_settings(ctxGlobals))

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
        # [wifi]
        # ssid = <some SSID>
        # security = WPA|WPA2|WEP|
        # password = <some wifi password>
        click.echo("\n--- [wifi] --------------------")
        click.echo("SSID:               {}".format(_get_option_val(settings, 'wifi', 'ssid')))
        click.echo("Security:           {}".format(_get_option_val(settings, 'wifi', 'security')))
        click.echo("Password:           {}".format(_get_option_val(settings, 'wifi', 'password')))

    if section in ['all', 'data']:
        # [data]
        # datadir = ~/workspace/wifi2           <-- Custom variable created by user by manually editing config
        # storage = CSV
        # host = ${datadir}/_temp_wifi2.csv     <-- Using Interpolatoin to pre-parse config file. Variable created by user
        # #storage = JSON
        # #host = ${datadir}/_temp_wifi2.json
        # #storage = SQLite
        # #host = ${datadir}/_temp_wifi2.sqlite
        # #storage = Influx
        # #host = localhost
        # port = 8086
        # dbuser = root
        # dbpswd = root
        # dbtable = SpeedTest                    <-- Should this be in next section?
        # dbname = SpeedTest
        click.echo("\n--- [data] --------------------")
        click.echo("DB Storage Type:          {}".format(_get_option_val(settings, 'data', 'storage')))
        click.echo("DB Host (server or file): {}".format(_get_option_val(settings, 'data', 'host')))
        click.echo("DB Port #:                {}".format(_get_option_val(settings, 'data', 'port')))
        click.echo("DB User  (dbuser:         {}".format(_get_option_val(settings, 'data', 'dbuser')))
        click.echo("DB Pswd  (dbpswd):        {}".format(_get_option_val(settings, 'data', 'dbpswd')))
        click.echo("DB Table (dbtable):       {}".format(_get_option_val(settings, 'data', 'dbtable')))
        click.echo("Database (db):      {}".format(_get_option_val(settings, 'data', 'db')))

    if section in ['all', 'test']:
        click.echo("\n--- [test] --------------------")
        # [speedtest]
        # uri = /home/cabox/.config/speedtest-cli
        # params
        # dbtable = SpeedTest
        # [ntwktest]
        # uri = /home/cabox/.config/ntwktest-cli
        # params
        # dbtable = NtwkTest
        click.echo("SpeedTest CLI URI:  {}".format(_get_option_val(settings, 'speedtest', 'uri')))
        click.echo("SpeedTest DB Table: {}".format(_get_option_val(settings, 'speedtest', 'dbtable')))
        click.echo("NtwkTest CLI URI:   {}".format(_get_option_val(settings, 'ntwktest', 'uri')))
        click.echo("NtwkTest DB Table:  {}".format(_get_option_val(settings, 'ntwktest', 'dbtable')))

    click.echo("\n-------------------------------")
    click.echo("CONFIG: '{}'\n".format(ctxGlobals['configFName']))
