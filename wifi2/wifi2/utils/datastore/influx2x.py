import os

from datetime import datetime
from urllib.parse import urlparse, urlsplit

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

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
#        I N F L U X   C L O U D   F U N C T I O N S
# =========================================================
def _connect_influxcloud_server(url, dbToken):
    try:
        dbClient = InfluxDBClient(url=url, token=dbToken)
        
    except Error as e:
        raise OSError("Failed to connect to Influx database '{}'\n{}!".format(host, e))
    
    return dbClient


def _process_influxcloud_data_row(rowIn, tblFlds, tblName):
    
    point = Point(tblName)

    point.time(rowIn['timestamp'], WritePrecision.NS)
    
    for key in tblFlds:
        if tblFlds[key] == 'field':
            point.field(key, rowIn[key])
        elif tblFlds[key] == 'tag':
            point.tag(key, rowIn[key])
                
    return point


def save_data(dataIn, url, tblFlds, tblName, dbBucket=None, dbOrgID=None, dbToken=None):
    
    if dbToken is None:
        raise ValueError("Missing token!")
        
    if dbOrgID is None:
        raise ValueError("Missing org ID!")
        
    if dbBucket is None:
        raise ValueError("Missing bucket name/ID!")
        
    dbClient = _connect_influxcloud_server(url, dbToken)
    dbWriter = dbClient.write_api(write_options=SYNCHRONOUS)
    
    dataPts = []
    for row in dataIn:
        dataPts.append(_process_influxcloud_data_row(row, tblFlds, tblName))
        
    dbWriter.write(dbBucket, dbOrgID, dataPts)
    
    dbClient.close()
    

def get_data(url, tblFlds, tblName, dbBucket=None, dbOrgID=None, dbToken=None, hours=1):
    
    def _process_table(table):
        record = {'timestamp': None, 'location': None, 'locationTZ': None, 'ping': None, 'upload': None, 'download': None}
        for row in table:
            if record['timestamp'] is None:
                record.update(timestamp = row.values['_time'].isoformat())
                
            if record['location'] is None:
                record.update(location = row.values['location'])
                
            if record['locationTZ'] is None:
                record.update(locationTZ = row.values['locationTZ'])
            
            fld = row.get_field()
            val = row.get_value()
            if record['ping'] is None and fld == 'ping':
                record.update(ping = val)
            elif record['upload'] is None and fld == 'upload':
                record.update(upload = val)
            elif record['download'] is None and fld == 'download':
                record.update(download = val)
            
        return record
    
    if dbToken is None:
        raise ValueError("Missing token!")
        
    if dbOrgID is None:
        raise ValueError("Missing org ID!")
        
    if dbBucket is None:
        raise ValueError("Missing bucket name/ID!")
        
    dbClient = _connect_influxcloud_server(url, dbToken)
    dbReader = dbClient.query_api()

    query = ('from(bucketID: "{0}") |> range(start: -{2}h) '
             '|> filter(fn: (r) => r._measurement == "{1}") '
             '|> filter(fn: (r) => r["_field"] == "download" or r["_field"] == "ping" or r["_field"] == "upload") '
             '|> group(columns: ["_time"])'
            ).format(dbBucket, tblName, hours)
    tables = dbReader.query(query=query, org=dbOrgID)
    
    data = []
    for table in tables:
        data.append(_process_table(table))
        
    dbClient.close()
    return data
