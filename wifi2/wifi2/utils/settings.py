import os
import click
import configparser
#from configparser import ConfigParser, ExtendedInterpolation, InterpolationMissingOptionError

_CSV_      = 'csv'
_JSON_     = 'json'
_SQLite_   = 'sqlite'
_SQL_      = 'sql'
_Influx1x_ = 'influx1x'
_Influx2x_ = 'influx2x'

import pprint
_PP_ = pprint.PrettyPrinter(indent=4)


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
    # @NOTE - we can only verify that values are stored
    #         in config, but not that they're correct.
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
# history = [1-100]                         - default num rec's to retrieve
# sort = [first|last]                       - retrieve first or last 'count' items
#
def _get_data_settings(ctxGlobals):
    datadir = click.prompt(
        "Enter path to common/default data folder",
        type=click.Path(),
        default='',
    )
    count = click.prompt(
        "Enter default for number of data records to retrieve:",
        type=click.IntRange(1, ctxGlobals['appHistory'], clamp=True),
        default=1,
        show_default=True,
    )
    sort = click.prompt(
        "Select default history list/sort order", 
        type=click.Choice(['first', 'last'], case_sensitive=False),
        default='first',
    )
    settings = {
        'data': {
            'datadir': datadir,
            'history': history,
            'sort': sort.lower(),
            }
        }
    
    return settings


def _validate_data_settings(settings):
    # 
    # @NOTE - there are no required items in this section 
    #         and we're only keeping this function to be 
    #         consistent with other config sections.
    # 
    return True


# ---------------------------------------------------------
#                Manage SpeedTest Settings
# ---------------------------------------------------------
#
# [<nameof test tool section>]
# count = [1-100]                       - num test cycle runs
# sleep = [1-60]                        - seconds between each test run
#
# threads = single|multi                - run single or multiple threads
# unit = bits|bytes                     - display speeds in Mbits/s or MB/s 
# share = yes|no                        - share test results
# location = <some location name>       - name of location where test computer is located
# locationTZ = <TZ name>                - Time zone at locatiomn (e.g. 'America/New York') 
#
# storage = CSV|JSON|SQLite|...         - data storage type
#           Influx1x|Influx2x
#
# host = <hostname or file path>        - data storage host. If file-based (i.e. CSV, JSON, SQLite),
#                                         then this is a path/filename)
#   Ex:     ~/speedtest.csv
#           ~/speedtest.json
#           ~/wifi2.sqlite              - SQLite file can hold several tables
#           http://localhost:8086       - SQL and Influx db servera can hold several databases. Should
#                                         also include port and protocal (http/https)
#
# dbtable = <db table name>             - Used for SQL, SQLite, and InfluxDB 1.x, v2.x
# dbname = <db name>                    - Used for SQL, SQLite, and InfluxDB 1.x
# dbuser = <db user w proper access>    - Used for SQL and InfluxDB 1.x
# dbpswd = <db user password>           - Used for SQL and InfluxDB 1.x
# dbretpol = <db retention policy>      - Used for InfluxDB 2.x
# dbbucket = <bucket ID>                - Used for InfluxDB 2.x
# dbtoken = <token instead of pswd>     - Used for InfluxDB 2.x
# dborgid = <organization ID>           - Used for InfluxDB 2.x
#
def _get_speedtest_settings(ctxGlobals):
    defaults = {
        'count': 1, 'sleep': 60, 'threads': 'multi', 'unit': 'bits', 'share': False, 
        'location': None, 'locationTZ': None, 
        'host': None, 'ssl': False, 
        'dbuser': 'wifi2_app', 'dbpswd': None, 'dbtoken': None, 
        'dbtable': 'SpeedTest', 'dbname': 'WIFI2_data', 'dbretpol': 'autogen',
        'dbbucket': None, 'dborgid': None,
    }
    
    count = click.prompt(
        "Enter default for number of test cycle runs:",
        type=click.IntRange(ctxGlobals['appMinRuns'], ctxGlobals['appMaxRuns'], clamp=True),
        default=ctxGlobals['appMinRuns'],
        show_default=True,
    )
    sleep = click.prompt(
        "Enter wait time (in seconds) between test cycle runs:",
        type=click.IntRange(1, 60, clamp=True),
        default=60,
        show_default=True,
    )
    
    threads = click.prompt(
        "Number of threads for SpeedTest", 
        type=click.Choice(['single', 'multi'], case_sensitive=False),
        default='multi',
        show_default=True,
    )
    unit = click.prompt(
        "Select speed rate unit per second", 
        type=click.Choice(['bits', 'bytes'], case_sensitive=False),
        default='bits',
        show_default=True,
    )
    share = click.prompt(
        "Share test results", 
        type=click.Choice(['yes', 'no'], case_sensitive=False),
        default='no',
        show_default=True,
    )
    location = click.prompt(
        "Name of location where test is run", 
    )
    locationTZ = click.prompt(
        "Name of (PYTZ) timezone for location", 
        default='America/New_York',
        show_default=True,
    )
    
    storage = click.prompt(
        "Enter data storage type", 
        type=click.Choice(['CSV', 'JSON', 'SQLite', 'SQL', 'Influx1x', 'Influx2x'], case_sensitive=False),
        default='SQLite',
        show_default=True,
    )
    
    if storage.lower() == _CSV_:
        settings = _get_speedtest_settings_CSV(defaults, ctxGlobals)
        
    elif storage.lower() == _JSON_:
        settings = _get_speedtest_settings_JSON(defaults, ctxGlobals)
        
    elif storage.lower() == _SQLite_:
        settings = _get_speedtest_settings_SQLite(defaults, ctxGlobals)
        
    elif storage.lower() == _SQL_:
        settings = _get_speedtest_settings_SQL(defaults, ctxGlobals)
        
    elif storage.lower() == _Influx1x_:
        settings = _get_speedtest_settings_Influx1x(defaults, ctxGlobals)
        
    elif storage.lower() == _Influx2x_:
        settings = _get_speedtest_settings_Influx2x(defaults, ctxGlobals)
        
    else:
        raise ValueError("Invalid storage type '{}'".format(storage))
        
    settings.update([
        ('count', count),
        ('sleep', sleep),
        ('threads', ('multi' if threads.lower() != 'single' else 'single')),
        ('unit', ('bits' if unit.lower() != 'bytes' else 'bytes')),
        ('share', (False if share.lower() != 'yes' else True)), 
        ('location', location),
        ('locationTZ', locationTZ),
    ])

    return {'speedtest': settings}


def _get_speedtest_settings_CSV(defaults, ctxGlobals):
    host = click.prompt(
        "Enter path to CSV data file",
        type=click.Path(),
        default=os.path.join(click.get_app_dir(ctxGlobals['appName']), dbTable.lower() + '.csv'),
        show_default=True,
    )

    return defaults.update([('host', host)])
    
    
def _get_speedtest_settings_JSON(defaults, ctxGlobals):
    host = click.prompt(
        "Enter path to JSON data file",
        type=click.Path(),
        default=os.path.join(click.get_app_dir(ctxGlobals['appName']), dbTable.lower() + '.json'),
        show_default=True,
    )

    return defaults.update([('host', host)])


def _get_speedtest_settings_SQLite(defaults, ctxGlobals):
    host = click.prompt(
        "Enter path to SQLite database.\nNote: ':memory:' is not supported.",
        type=click.Path(),
        default=os.path.join(click.get_app_dir(ctxGlobals['appName']), dbName.lower() + '.sqlite'),
        show_default=True,
    )
    dbtable = click.prompt(
        "Enter name of database table",
        default=defaults['dbtable'],
        show_default=True,
    )

    return defaults.update([('host', host), ('dbtable', dbtable)])


def _get_speedtest_settings_SQL(defaults, ctxGlobals):
    host = click.prompt("Enter database URL (protocal, host, and port)",
        default='http://localhost:8086',
        show_default=True,
    )
    dbuser = click.prompt("Enter database user name")
    dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
    dbtoken = click.prompt("Enter JWT token", default='')
    dbtable = click.prompt(
        "Enter name of database table",
        default=dbTable,
        show_default=True,
    )
    dbname = click.prompt(
        "Enter name of database",
        default=dbname,
        show_default=True,
    )

    return defaults.update([
        ('host', host), ('dbtable', dbtable), ('dbname', dbname), 
        ('dbuser', dbuser), ('dbpswd', dbpswd), ('dbtoken', dbtoken)
    ])


def _get_speedtest_settings_Influx1x(defaults, ctxGlobals):
    host = click.prompt("Enter database URL (protocal, host, and port)",
        default='http://localhost:8086',
        show_default=True,
    )
    dbuser = click.prompt("Enter database user name")
    dbpswd = click.prompt("Enter database user password", default='', hide_input=True)
    dbtoken = click.prompt("Enter JWT token", default='')
    dbtable = click.prompt(
        "Enter name of database table",
        default=dbtable,
        show_default=True,
    )
    dbname = click.prompt(
        "Enter name of database",
        default=dbname,
        show_default=True,
    )
    dbretpol = click.prompt(
        "Enter name of database retention policy",
        default=dbretpol,
        show_default=True,
    )

    return defaults.update([
        ('host', host), ('dbtable', dbtable), ('dbname', dbname), ('dbretpol', dbretpol),
        ('dbuser', dbuser), ('dbpswd', dbpswd), ('dbtoken', dbtoken)
    ])


def _get_speedtest_settings_Influx2x(defaults, ctxGlobals):
    host = click.prompt("Enter database URL (protocal, host, and port)",
        default='http://localhost:8086',
        show_default=True,
    )
    dbtoken = click.prompt("Enter InfluxDB token", default='')
    dbtable = click.prompt(
        "Enter name of database table",
        default=dbtable,
        show_default=True,
    )
    dbbucket = click.prompt("Enter InfluxDB 'bucket' ID", default='')
    dborgid = click.prompt("Enter InfluxDB org ID", default='')
        
    return defaults.update(
        ('host', host), ('dbtable', dbtable), ('dbbucket', dbbucket),
        ('dborgid', dborgid), ('dbtoken', dbtoken)
    )


def _validate_speedtest_settings(settings):
    #
    # @NOTE - we can only verify that values are stored
    #         in config, but not that they're correct.
    #
    if not settings.has_option('speedtest', 'host'):
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
# sleep = [1-60]                        - seconds between each test run
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
# --
#            'appName': APP_NAME,
#            'configFName': os.path.expanduser(config),
#            'appMinRuns': APP_MIN_RUNS,
#            'appMaxRuns': APP_MAX_RUNS,
#            'appHistory': APP_HISTORY,
#            'appSleep': APP_SLEEP,
# --                
def _get_sometest_settings(ctxGlobals):
    uri = click.prompt(
        "Enter URI for 'sometest-cli'",
        type=click.Path(),
        default=click.get_app_dir('sometest-cli')
    )
    params = None
    count = click.prompt(
        "Enter default for number of test cycle runs:",
        type=click.IntRange(ctxGlobals['appMinRuns'], ctxGlobals['appMaxRuns'], clamp=True),
        default=ctxGlobals['appMinRuns'],
        show_default=True,
    )
    sleep = click.prompt(
        "Enter wait time (in seconds) between test cycle runs:",
        type=click.IntRange(1, 60, clamp=True),
        default=60,
        show_default=True,
    )
    
    settings = {
        'sometest': {
            'URI': uri,
            'params': params,
            'count': count,
            'sleep': sleep,
            }
        }
    
    # /usr/local/bin/????
    
    return settings


def _validate_sometest_settings(settings):
    #
    # @NOTE - we can only verify that values are stored
    #         in config, but not that they're correct.
    #
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
        try:
            config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), allow_no_value=True)
            config.read(ctxGlobals['configFName'])
        except configparser.Error as e:
            raise ValueError("Invalid configuration settings!\n{}".format(e))
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

    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), allow_no_value=True)
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
            try:
                if _settings.has_option(_section, _option):
                    outStr = str(_settings[_section][_option])
            except configparser.Error:
                outStr = '- Invalid setting! -'

        return outStr

    if not section.lower() in ['wifi', 'data', 'test', 'all']:
        raise ValueError("Invalid section '{}'".format(section))
        
    settings = read_settings(ctxGlobals)
    
    if section in ['all', 'wifi']:
        #
        # [wifi]
        # ssid = <some SSID>
        # security = WPA|WPA2|WEP
        # password = <some wifi password>
        #
        click.echo("\n--- [wifi] --------------------")
        click.echo("SSID:               {}".format(_get_option_val(settings, 'wifi', 'ssid')))
        click.echo("Security:           {}".format(_get_option_val(settings, 'wifi', 'security')))
        click.echo("Password:           {}".format(_get_option_val(settings, 'wifi', 'password')))

    if section in ['all', 'data']:
        # [data]
        # datadir = <common folder for data files>  - e.g. ~/wifi2/data
        # history = [1-100]                         - default num rec's to retrieve
        # sort = [first|last]                       - retrieve first or last 'count' items
        #
        click.echo("\n--- [data] --------------------")
        click.echo("Common Data Dir:    {}".format(_get_option_val(settings, 'data', 'datadir')))
        click.echo("Default History:    {}".format(_get_option_val(settings, 'data', 'history')))
        click.echo("Default Sort:       {}".format(_get_option_val(settings, 'data', 'sort')))

    if section in ['all', 'test']:
        click.echo("\n--- [test] --------------------")
        # [<nameof test tool section>]
        # uri = <uri/path to test tool>         - USED AS NEEDED -
        # params = <any test tool params>       - USED AS NEEDED -
        # count = [1-100]                       - num test cycle runs
        # sleep = [1-60]                        - seconds between each test run
        #
        # threads = single|multi                - run single or multiple threads
        # unit = bits|bytes                     - display speeds in Mbits/s or MB/s 
        # share = yes|no                        - share test results
        # location = <some location name>       - name of location where test computer is located
        # locationTZ = <TZ name>                - Time zone at locatiomn (e.g. 'America/New York') 
        #
        # storage = CSV|JSON|SQLite|...         - data storage type
        #           Influx1x|InfluxCloud
        #
        # host = <hostname or file path>        - data storage host. If file-based (i.e. CSV, JSON, SQLite),
        #                                         then this is a path/filename)
        #   Ex:     ~/speedtest.csv
        #           ~/speedtest.json
        #           ~/wifi2.sqlite              - SQLite file can hold several tables
        #           http://localhost:8086       - Influx db server can hold several databases. Should also
        #                                         include port and protocal (http/https)
        #
        # token = <token instead of user pswd>  - Used for InfluxDB Cloud
        # dbuser = <db user w proper access>    - Used for InfluxDB 1.x and Cloud
        # dbpswd = <db user password>           - Used for InfluxDB 1.x
        # dbtable = <db table name>             - Used for SQLite and all InfluxDB
        # dbname = <db name>                    - Used for SQLite and all InfluxDB 
        # dbretpol = <db retention policy>      - Used for InfluxDB Cloud
        #
        click.echo("SpeedTest Settings")
        click.echo("  Test Run Count:   {}".format(_get_option_val(settings, 'speedtest', 'count')))
        click.echo("  Sleep/Wait Time:  {}".format(_get_option_val(settings, 'speedtest', 'sleep')))
        click.echo("  Threads:          {}".format(_get_option_val(settings, 'speedtest', 'threads')))
        click.echo("  Speed Rate Unit:  {}".format(_get_option_val(settings, 'speedtest', 'units')))
        click.echo("  Share Results:    {}".format(_get_option_val(settings, 'speedtest', 'share')))
        click.echo("  Location Name:    {}".format(_get_option_val(settings, 'speedtest', 'location')))
        click.echo("  Location TZ:      {}".format(_get_option_val(settings, 'speedtest', 'locationTZ')))
        click.echo("  DB Storage Type:  {}".format(_get_option_val(settings, 'speedtest', 'storage')))
        click.echo("  DB Host:          {}".format(_get_option_val(settings, 'speedtest', 'host')))
        click.echo("  DB User:          {}".format(_get_option_val(settings, 'speedtest', 'dbuser')))
        click.echo("  DB User Password: {}".format(_get_option_val(settings, 'speedtest', 'dbpswd')))
        click.echo("  DB Table:         {}".format(_get_option_val(settings, 'speedtest', 'dbtable')))
        click.echo("  DB Name:          {}".format(_get_option_val(settings, 'speedtest', 'dbname')))
        click.echo("  DB Ret Policy:    {}".format(_get_option_val(settings, 'speedtest', 'dbretpol')))
        click.echo("  DB Token:         {}".format(_get_option_val(settings, 'speedtest', 'dbtoken')))
        click.echo("  DB Bucket:        {}".format(_get_option_val(settings, 'speedtest', 'dbbucket')))
        click.echo("  DB Org ID:        {}".format(_get_option_val(settings, 'speedtest', 'orgid')))
        
        click.echo("\nSome Other Test Settings")
        click.echo("  CLI URI:          {}".format(_get_option_val(settings, 'sometest', 'uri')))
        click.echo("  CLI params:       {}".format(_get_option_val(settings, 'sometest', 'params')))

    click.echo("\n-------------------------------")
    click.echo("CONFIG: '{}'\n".format(ctxGlobals['configFName']))
