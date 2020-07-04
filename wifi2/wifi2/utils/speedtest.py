import re
import subprocess
import time

from .datastore import save_csv_data, get_csv_data, save_json_data, get_json_data
from .datastore import save_sqlite_data, get_sqlite_data, save_influx_data, get_influx_data


# =========================================================
#          S P E E D T E S T   F U N C T I O N S
# =========================================================
def run_speed_test(settings):
    """Run speed test on current internet connection to get data points for PING, UP-and DOWNLOAD speeds.
    
    Args:
        settings: list with application settings
        
    Returns:
        Dict record with timestamp, ping, download, and upload times.
        
    Raises:
        OSError: If 'speedtest-cli' sub-process cannot run and/or exits with non-zero error code.
    """
    try:
        proc = subprocess.Popen('speedtest-cli --simple',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        
    except OSError as e:
        raise OSError("Failed to run 'speedtest-cli' utility! [Orig: {}]".format(e))

    proc.wait() 
    if proc.returncode != 0:
        raise OSError("Failed to run and/or missing 'speedtest-cli' utility! [Code: {}]".format(str(proc.returncode)))
        
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
def save_speed_data(settings, data):
    """Save SpeedTest data to preferred data store as defined in application settings.
    
    Args:
        settings: Data store settings
        data:     List with data rows

    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """

    def _csv_data_header():
        return 'time,ping,download,upload\r\n'

    def _csv_data_formatter(dataRow):
        return '{},{},{},{}\r\n'.format(dataRow['time'], dataRow['ping'], dataRow['download'], dataRow['upload'])

    if settings['storage'].lower() == 'csv':
        save_csv_data(settings['db'], data, _csv_data_formatter, _csv_data_header)
        
    elif settings['storage'].lower() == 'json':
        save_json_data(settings['db'], data)
        
    elif settings['storage'].lower() == 'sqlite':
        save_sqlite_data(settings['db'], data)
        
    elif settings['storage'] == 'Influx':
        save_influx_data(settings['db'], settings['dbuser'], settings['dbpswd'], data)
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings['storage'])))

        
def get_speed_data(settings, numRecs, first=True):
    """Retrieve SpeedTest data records from preferred data store as defined in application settings.
    
    Args:
        settings: List with data store settings
        numRecs:  Number of records to retrieve
        first:    If TRUE, retrieve first 'numRec' records, else retrieve last 'numRec' records
    
    Returns:
        List of data records
        
    Raises:
        OSError: If data store is not supported and/or cannot be accessed.
    """
    if settings['storage'].lower() == 'csv':
        return get_csv_data(settings['db'], numRecs, first)
        
    elif settings['storage'].lower() == 'json':
        return get_json_data(settings['db'], numRecs, first)
        
    elif settings['storage'].lower() == 'sqlite':
        return get_sqlite_data(settings['db'], numRecs, first)
        
    elif settings['storage'] == 'Influx':
        return get_influx_data(settings['db'], settings['dbuser'], settings['dbpswd'], numRecs, first)
        
    else:    
        raise OSError("Data storage type '{}' is not supported!".format(str(settings['storage'])))
