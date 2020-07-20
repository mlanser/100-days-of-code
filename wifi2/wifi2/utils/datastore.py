import os
import csv
import json
import sqlite3

from datetime import datetime
from urllib.parse import urlparse, urlsplit

from influxdb import InfluxDBClient as InfluxDBv1
from influxdb.exceptions import InfluxDBClientError as InfluxDBv1ClientError

from influxdb_client import InfluxDBClient as InfluxDBv2, Point, WritePrecision
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
#                  C S V   F U N C T I O N S
# =========================================================
def save_csv_data(data, dbFName, dbFlds, force=True):
    """Save data to CSV file.
    
    Args:
        data:    List with one or more data rows
        dbFName: CSV file name
        dbFlds:  Dict with field names (as keys) and data types
        force:   If TRUE, CSV file will be created if it doesn't exist

    Raises:
        OSError: If unable to access or save data to CSV file.
    """

    if not os.path.exists(dbFName):
        if force:
            _make_path(dbFName)
        else:
            raise OSError("CSV data file '{}' does not exist!".format(dbFName))
    
    with open(dbFName, 'a+', newline='') as dbFile:
        dataWriter = csv.DictWriter(dbFile, dbFlds.keys(), extrasaction='ignore')

        try:
            if os.stat(dbFName).st_size == 0:
                dataWriter.writeheader()

            for row in data:
                dataWriter.writerow(row)

        except csv.Error as e:
            raise OSError("Failed to save data to '{}'!\n{}".format(dbFName, e))
    

def get_csv_data(dbFName, dbFlds, numRecs=1, first=True):
    """Retrieve data from CSV file.
    
    Args:
        dbFName:  CSV file name
        dbFlds:   Dict with field names (as keys) and data types
        numRecs:  Number of records to retrieve
        first:    If TRUE, retrieve first 'numRecs' records. Else retrieve last 'numRecs' records.

    Raises:
        OSError: If unable to access or read data from CSV file.
    """

    def _row_counter(fp):
        for cntr, row in enumerate(fp, 0):              # Count all lines/rows ...
            pass
        fp.seek(0)                                      # ... and 'rewind' file to beginning
        
        return cntr

    def _process_row(rowIn, flds):
        rowOut = {}
        for key, val in rowIn.items():
            if key in flds:
                rowOut.update({key : flds[key](val)})
    
        return rowOut
    
    data = []
    with open(dbFName, 'r', newline='') as dbFile:
        lastRec = numRecs if first else _row_counter(dbFile)
        firstRec = 1 if first else max(1, lastRec - numRecs + 1)
        
        dataReader = csv.DictReader(dbFile, dbFlds.keys())

        try:    
            for i, row in enumerate(dataReader, 0):
                if i < firstRec:
                    continue;
                elif i > lastRec:
                    break
                else:    
                    data.append(_process_row(row, dbFlds))

        except csv.Error as e:
            raise OSError("Failed to read data from '{}'!\n{}".format(dbFName, e))

        if len(data) < 1:    
            raise OSError("Empty data file")
            
    return data

    
# =========================================================
#                 J S O N   F U N C T I O N S
# =========================================================
def _read_json(dbFName):
    try:
        dbFile = open(dbFName, "r")
        data = json.load(dbFile)
        
    except json.JSONDecodeError:    # We'll just 'overwrite' the file
        return None                 # if it's empty or if we can't read it.

    else:
        dbFile.close()
    return data

        
def _write_json(dbFName, data):
    try:
        dbFile = open(dbFName, "w")
        json.dump(data, dbFile)
        
    except OSError as e:
        raise OSError("Failed to write data to '{}'!\n{}".format(dbFName, e))
        
    else:
        dbFile.close()
    
    
def save_json_data(data, dbFName, dbFlds, force=True):
    """Save data to JSON file.

    Args:
        data:    List with one or more data rows
        dbFName: JSON file name
        dbFlds:  Dict with field names (as keys) and data types
        force:   If TRUE, JSON file will be created if it doesn't exist

    Raises:
        OSError: If unable to access or save data to JSON file.
    """

    if not os.path.exists(dbFName):
        if force:
            _make_path(dbFName)
        else:
            raise OSError("JSON data file '{}' does not exist!".format(dbFName))
            
    try:
        oldData = _read_json(dbFName) if os.path.exists(dbFName) else None
        newData = _process_data(data, dbFlds.keys())

        _write_json(dbFName, newData if oldData is None else oldData + newData)

    except OSError as e:
        raise OSError("Failed to access '{}'!\n{}".format(dbFName, e))


def get_json_data(dbFName, dbFlds, numRecs=1, first=True):
    """Retrieve data from JSON file.

    Args:
        dbFName: JSON file name
        dbFlds:  Dict with field names (as keys) and data types
        numRecs: Number of records to retrieve
        first:   If TRUE, retrieve first 'numRecs' records. Else retrieve last 'numRecs' records.

    Raises:
        OSError: If unable to access or read data from JSON file.
    """

    try:
        jsonData = _read_json(dbFName) if os.path.exists(dbFName) else None

        if jsonData is None:
            data = []
        else:
            lastRec = numRecs if first else len(jsonData)
            firstRec = 0 if first else max(0, lastRec - numRecs)
            data = _process_data(jsonData[firstRec:lastRec], dbFlds.keys())

    except OSError as e:
        raise OSError("Failed to read data from '{}'!\n{}".format(dbFName, e))

    return data


# =========================================================
#               S Q L I T E   F U N C T I O N S
# =========================================================
def _connect_sqlite(dbFName, force=True):
    if not os.path.exists(dbFName):
        if force:
            _make_path(dbFName)
        else:
            raise OSError("SQLite data file '{}' does not exist!".format(dbFName))
            
    try:
        dbConn = sqlite3.connect(dbFName)
        
    except sqlite3.Error as e:
        raise OSError("Failed to connect to SQLite database '{}'\n{}!".format(dbFName, e))
    
    return dbConn


def _exist_sqlite_table(dbCur, tblName):
    """Check if a table with a given name exists.

    Note that SQLIte3 stores table names in the 'sqlite_master' table.

    Args:
        dbCur:   DB cursor for a given database connection
        tblName: Table name to look for

    Returns:
        bool:    TRUE if table exists, Else FALSE.
    """

    dbCur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}'".format(tblName))

    return True if dbCur.fetchone()[0] == 1 else False


def _create_sqlite_table(dbCur, tblName, fldNamesWithTypes):
    """Create table with fields.

    Args:
        dbCur:   DB cursor for a given database connection
        tblName: Table name to look for
        fldNamesWithTypes: Dictionary with field names and associated SQLite data types
    """

    flds = ','.join("{!s} {!s}".format(key, val) for (key, val) in fldNamesWithTypes.items())

    dbCur.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(tblName, flds))


def save_sqlite_data(data, dbFName, tblFlds, tblName, force=True):
    """Save data to SQLite database.

    Args:
        data:    List with one or more data rows
        dbFName: File name for SQLite database
        tblFlds: Dict w DB field names and data types
        tblName: DB table name
        force:   If TRUE, SQLite file will be created if it doesn't exist
    """

    dbConn = _connect_sqlite(dbFName, force)
    dbCur = dbConn.cursor()

    if not _exist_sqlite_table(dbCur, tblName):
        _create_sqlite_table(dbCur, tblName, tblFlds)
    
    fldNames = tblFlds.keys()
    flds = ','.join(fldNames)
    vals = ','.join("?" for (_) in fldNames)
    for row in data:
        # Using list comprehension to only pull values 
        # that we want/need from a row of data
        dbCur.execute("INSERT INTO {}({}) VALUES({})".format(tblName, flds, vals),
                      [row[key] for key in fldNames])

    dbConn.commit()
    dbConn.close()


def get_sqlite_data(dbFName, tblFlds, tblName, orderBy=None, numRecs=1, first=True):
    """Retrieve 'numrec' data records from SQLite database.

    Args:
        dbFName:  File name for SQLite database
        tblFlds:  Dict w DB field names and data types
        tblName:  DB table name
        orderBy:  Field to sorted by
        numRecs:  Number of records to retrieve
        first:    If TRUE, rerieve first 'numRec' records, else retrieve last 'numRec' records.

    Returns:
        list:     List of all records retrieved
    """

    def _flip_orderby(inStr, flip=False):
        if inStr == 'ASC':
            return 'ASC' if not flip else 'DESC'
        else:
            return 'DESC' if not flip else 'ASC'
        
        
    def _create_orderby_param(inStr, flip=False):
        parts = inStr.split('|')
        
        if len(parts) < 1:
            return ''
        
        outStr = 'ASC' if len(parts) == 1 else parts[1].upper()
        return 'ORDER BY {} {}'.format(parts[0], _flip_orderby(outStr, flip))
    
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()
    
    fldNames = tblFlds.keys()
    flds = ','.join("{!s}".format(key) for key in fldNames)
    sortFld = list(fldNames)[0] if orderBy is None else orderBy
        
    if first:
        dbCur.execute('SELECT {flds} FROM {tbl} {order} LIMIT {limit}'.format(
            flds=flds,
            tbl=tblName,
            order=_create_orderby_param(sortFld),
            limit=numRecs
        ))
    else:    
        dbCur.execute('SELECT * FROM (SELECT {flds} FROM {tbl} {inner} LIMIT {limit}) {order}'.format(
            flds=flds,
            tbl=tblName,
            inner=_create_orderby_param(sortFld, True),
            limit=numRecs,
            order=_create_orderby_param(sortFld)
        ))
    
    dataRecords = dbCur.fetchall()
    dbConn.close()

    data = []
    for row in dataRecords:
        # Create dictionary with keys from field name 
        # list, mapped against vaues from database.
        data.append(dict(zip(tblFlds.keys(), row)))

    return data

    
# =========================================================
#           I N F L U X   1.X   F U N C T I O N S
# =========================================================
def _connect_influx1x_server(url, dbUser, dbPswd, dbName):
    urlParts = urlsplit(url)
    
    try:
        dbClient = InfluxDBv1(urlParts.hostname, urlParts.port, dbUser, dbPswd, dbName)
        
    except InfluxDBv1ClientError as e:
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


def save_influx1x_data(dataIn, url, tblFlds, tblName, dbName, dbUser, dbPswd):
    
    dbClient = _connect_influx1x_server(url, dbUser, dbPswd, dbName)
    
    if not _exist_influx1x_database(dbClient, dbName):
        raise OSError("Missing Influx database '{}'\n!".format(dbName))
    
    dataPts = []
    for row in dataIn:
        dataPts.append(_process_influx1x_data_row(row, tblFlds, tblName))
    
    if not dbClient.write_points(dataPts):
        raise OSError("Failed to save data to Influx database '{}' on host '{}'!".format(dbName, host))
    
    dbClient.close()
    
    
def get_influx1x_data(url, tblFlds, tblName, dbName, dbUser, dbPswd, numRecs=1, first=True):
    
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


# =========================================================
#        I N F L U X   C L O U D   F U N C T I O N S
# =========================================================
def _connect_influxcloud_server(url, dbToken):
    try:
        dbClient = InfluxDBv2(url=url, token=dbToken)
        
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


def save_influxcloud_data(dataIn, url, tblFlds, tblName, dbBucket=None, dbOrgID=None, dbToken=None):
    
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
    

def get_influxcloud_data(url, tblFlds, tblName, dbBucket=None, dbOrgID=None, dbToken=None, hours=1):
    
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
