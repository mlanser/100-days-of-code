import speedtest

from .datastore import save_csv_data, get_csv_data, save_json_data, get_json_data
from .datastore import save_sqlite_data, get_sqlite_data, save_influx1x_data, get_influx1x_data, save_influxcloud_data, get_influxcloud_data

_DB_NAME_   = 'WIFI2_data'
_DB_RETPOL_ = 'autogen'
_DB_TABLE_  = 'SpeedTest'
_DB_ORDER_  = 'timestamp|ASC'
_DB_FLDS_   = {
    'raw':    {'timestamp': str, 'location': str, 'locationTZ': str, 'ping': float, 'download': float, 'upload': float},
    'csv':    {'timestamp': None, 'location': None, 'locationTZ': None, 'ping': None, 'download': None, 'upload': None},
    'json':   {'timestamp': None, 'location': None, 'locationTZ': None, 'ping': None, 'download': None, 'upload': None},
    'sqlite': {'timestamp': 'TEXT', 'location': 'TEXT', 'locationTZ': 'TEXT', 'ping': 'REAL', 'download': 'REAL', 'upload': 'REAL'},
    'influx': {'timestamp': 'time', 'location': 'tag', 'locationTZ': 'tag', 'ping': 'field', 'download': 'field', 'upload': 'field'},
}

import pprint
_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#          S P E E D T E S T   F U N C T I O N S
# =========================================================
def run_speedtest(settings):
    """Run speed test on current internet connection to get data points for PING, UP-and DOWNLOAD speeds.
    
    Args:
        settings: list with SpeedTest settings
        
    Returns:
        Dict record with timestamp, ping time, download and upload speeds (bits/s), and more.
        
    Raises:
        SpeedtestException: If 'speedtest' failed to run or experienced failure during test run.
    """
    
    # If we want to run test against a specific server,
    # then add server ID
    # i.e. servers = [1234]
    servers = []

    # If we want to run single-threaded test, then set to "1"
    threads = None if settings.get('threads', None).lower() != 'single' else 1

    test = speedtest.Speedtest()
    test.get_servers(servers)
    test.get_best_server()
    test.download(threads=threads)
    test.upload(threads=threads, pre_allocate=False)
    
    if settings.getboolean('share', False):
        test.results.share()
        
    response = test.results.dict()
    response.update([
        ('location', settings.get('location')),
        ('locationTZ', settings.get('locationTZ'))
    ])
    
    return response


# =========================================================
#                D A T A   F U N C T I O N S
# =========================================================
def save_speed_data(settings, data):
    """Save SpeedTest data to preferred data store as defined in application settings.
    
    Args:
        settings: Data store settings
        data:     List with data rows

    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """

    #print('\n-- [settings] --')
    #_PP_.pprint(settings)
    #print('\n-- [data] ------')
    #_PP_.pprint(data)
    #print('----------------\n')
    
    if settings.get('storage').lower() == 'csv':
        save_csv_data(data, settings.get('host'), _DB_FLDS_['csv'])
        
    elif settings.get('storage').lower() == 'json':
        save_json_data(data, settings.get('host'), _DB_FLDS_['json'])
        
    elif settings.get('storage').lower() == 'sqlite':
        save_sqlite_data(data, settings.get('host'), _DB_FLDS_['sqlite'], settings.get('dbtable', _DB_TABLE_))
        
    elif settings.get('storage').lower() == 'influx1x':
        save_influx1x_data(data, settings.get('host'), _DB_FLDS_['influx'], settings.get('dbtable', _DB_TABLE_), 
                           settings.get('dbname', _DB_NAME_), settings.get('dbuser'), settings.get('dbpswd')
                          )
        
    elif settings.get('storage').lower() == 'influx2x':
        save_influxcloud_data(data, settings.get('host'), _DB_FLDS_['influx'], settings.get('dbtable', _DB_TABLE_),
                              settings.get('dbbucket', None), settings.get('dborgid', None), settings.get('dbtoken', None)
                             )
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings['storage'])))

        
def get_speed_data(settings, numRecs, first=True):
    """Retrieve SpeedTest data records from preferred data store as defined in application settings.
    
    Args:
        settings: List with data store settings
        numRecs:  Number of records to retrieve
                  NOTE: for InfluxDB v2.x this represents last X hours
        
        first:    If TRUE, retrieve first 'numRec' records, else retrieve last 'numRec' records
                  NOTE: this is not used for InfluxDB v2.x
    
    Returns:
        List of data records
        
    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """
    
    if settings.get('storage').lower() == 'csv':
        return get_csv_data(settings.get('host'), _DB_FLDS_['raw'], numRecs, first)
        
    elif settings.get('storage').lower() == 'json':
        return get_json_data(settings.get('host'), _DB_FLDS_['raw'], numRecs, first)
        
    elif settings.get('storage').lower() == 'sqlite':
        return get_sqlite_data(settings.get('host'), _DB_FLDS_['raw'], settings.get('dbtable', _DB_TABLE_), _DB_ORDER_, numRecs, first)
        
    elif settings.get('storage').lower() == 'influx1x':
        return get_influx1x_data(settings.get('host'), _DB_FLDS_['influx'], settings.get('dbtable', _DB_TABLE_),  
                               settings.get('dbname', _DB_NAME_), settings.get('dbuser'), settings.get('dbpswd'),
                               numRecs, first
                              )
        
    elif settings.get('storage').lower() == 'influx2x':
        return get_influxcloud_data(settings.get('host'), _DB_FLDS_['influx'], settings.get('dbtable', _DB_TABLE_),
                                    settings.get('dbbucket', None), settings.get('dborgid', None), settings.get('dbtoken', None), 
                                    numRecs
                                   )
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings.get('storage'))))
