import os

from datetime import datetime
from urllib.parse import urlparse, urlsplit

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError as InfluxDBClientClientError

import pprint
_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _process_data(dataIn, fldNames):
    dataOut = []

    for row in dataIn:
        # Filter each row to only hold approved keys using dictionary comprehension
        dataOut.append({key: row[key] for key in fldNames})

    return outData


def _make_path(fname):
    try:
        path = os.path.dirname(os.path.abspath(fname))
        if not os.path.exists(path):
            os.makedirs(path)

    except OSError as e:
        raise OSError("Failed to create path '{}'!\n{}".format(path, e))


# =========================================================
#           I N F L U X   1.X   F U N C T I O N S
# =========================================================
def _connect_influx1x_server(url, dbUser, dbPswd, dbName):
    urlParts = urlsplit(url)
    
    try:
        dbClient = InfluxDBClient(urlParts.hostname, urlParts.port, dbUser, dbPswd, dbName)
        
    except InfluxDBClientClientError as e:
        raise OSError("Failed to connect to Influx database '{}'\n{}!".format(host, e))
    
    return dbClient


def _exist_influx1x_database(dbClient, dbName):
    for item in dbClient.get_list_database():
        if item['name'] == dbName:
            return True

    return False


def _process_influx1x_data_row(rowIn, tblFlds, tblName):
    point = {'measurement': tblName, 'time': rowIn['timestamp'], 'tags': {}, 'fields': {}}
    
    for key in tblFlds:
        if tblFlds[key] == 'field':
            point['fields'].update({key:rowIn[key]})
        elif tblFlds[key] == 'tag':
            point['tags'].update({key:rowIn[key]})
    
    return point


def _resort_influx1x_records(dataIn):
    
    def _get_key_val(item):
        return item.get('timestamp')

    return sorted(dataIn, key=_get_key_val)


def save_data(dataIn, url, tblFlds, tblName, dbName, dbUser, dbPswd):
    
    dbClient = _connect_influx1x_server(url, dbUser, dbPswd, dbName)
    
    if not _exist_influx1x_database(dbClient, dbName):
        raise OSError("Missing Influx database '{}'\n!".format(dbName))
    
    dataPts = []
    for row in dataIn:
        dataPts.append(_process_influx1x_data_row(row, tblFlds, tblName))
    
    if not dbClient.write_points(dataPts):
        raise OSError("Failed to save data to Influx database '{}' on host '{}'!".format(dbName, host))
    
    dbClient.close()
    
    
def get_data(url, tblFlds, tblName, dbName, dbUser, dbPswd, numRecs=1, first=True):
    
    dbClient = _connect_influx1x_server(url, dbUser, dbPswd, dbName)
    
    if not _exist_influx1x_database(dbClient, dbName):
        raise OSError("Missing Influx database '{}'\n!".format(dbName))
    
    # Get fields and tags, and remember to rename 'time' to 'timestamp' 
    # as InfluxDB uses 'time' as record ID in the timeseries database
    flds = ','.join("{!s}".format(key) for key in tblFlds.keys()).replace('timestamp', 'time as timestamp')

    qryResult = dbClient.query('SELECT {flds} FROM {tbl} ORDER BY "time" {sort} LIMIT {limit}'.format(
                               flds=flds, 
                               tbl=tblName, 
                               sort='ASC' if first else 'DESC', 
                               limit=numRecs)
                              )
    data = []
    dataRecs = qryResult.raw['series'][0]['values']         # InfluxQL query returns complex result set
    keys = qryResult.raw['series'][0]['columns']            # where we need to pull out specific items
    for row in dataRecs:
        # Create dictionary with keys from field name 
        # list, mapped against vaues from database.
        data.append(dict(zip(keys, row)))
    
    dbClient.close()
    return data if first else _resort_influx1x_records(data)
