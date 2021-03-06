import os
import re
import subprocess
import time
#import click
#import sys

from .datastore import save_csv_data, get_csv_data, save_json_data, get_json_data
from .datastore import save_sqlite_data, get_sqlite_data, save_influx_data, get_influx_data


# =========================================================
#          S P E E D T E S T   F U N C T I O N S
# =========================================================
def run_ntwk_test(settings):
    # @TODO Finish this function
    """Run tests on current network connection to get misc data points.
    
    Args:
        settings: list with application settings
        
    Returns:
        Dict record with ???
        
    Raises:
        OSError: If '???' sub-process cannot run and/or exits with non-zero error code.
    """
    try:
        proc = subprocess.Popen('ntwktest-cli --simple',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        
    except OSError as e:
        raise OSError("Failed to run 'ntwktest-cli' utility! [Orig: {}]".format(e))

    proc.wait() 
    if proc.returncode != 0:
        raise OSError("Failed to run and/or missing 'ntwktest-cli' utility! [Code: {}]".format(str(proc.returncode)))
        
    response = proc.stdout.read()
    
    timeStamp = time.time()
    ping = re.findall('Ping:\s(.*?)\s', str(response), re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', str(response), re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', str(response), re.MULTILINE)

    return {
        'time': timeStamp,
        'ping': ping[0].replace(',', '.'),
        'download': download[0].replace(',', '.'),
        'upload': upload[0].replace(',', '.'),
    }


# =========================================================
#                D A T A   F U N C T I O N S
# =========================================================
def save_ntwk_data(settings, data, dataFmt = None, dataHdr = None):
    # @TODO Finish this function
    """Save ntwkTest data to preferred data store as defined in application settings.
    
    Args:
        settings: list with data store settings
        dataFmt:  optional data row formatter callback function (e.g. to format CSV record string)
        dataHdr:  potional data header row string (e.g. for CSV data/column headers)
        
    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """
    if settings['storage'].lower() == 'csv':
        save_csv_data(settings['db'], data, dataFmt, dataHdr)
        
    elif settings['storage'].lower() == 'json':
        save_json_data(settings['db'], data)
        
    elif settings['storage'].lower() == 'sqlite':
        save_sqlite_data(settings['db'], data)
        
    elif settings['storage'] == 'Influx':
        save_influx_data(settings['db'], settings['dbuser'], settings['dbpswd'], data)
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings['storage'])))

        
def get_ntwk_data(settings, count):
    # @TODO Finish this function
    """Retrieve ntwkTest data records from preferred data store as defined in application settings.
    
    Args:
        settings: list with data store settings
        count:    number of records to retrieve
        
    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """
    if settings['storage'].lower() == 'csv':
        get_csv_data(settings['db'], count)
        
    elif settings['storage'].lower() == 'json':
        get_json_data(settings['db'], count)
        
    elif settings['storage'].lower() == 'sqlite':
        get_sqlite_data(settings['db'], count)
        
    elif settings['storage'] == 'Influx':
        get_influx_data(settings['db'], settings['dbuser'], settings['dbpswd'], count)
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings['storage'])))
