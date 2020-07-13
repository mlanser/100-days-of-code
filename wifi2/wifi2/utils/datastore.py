import os
import csv
import json
import sqlite3
from influxdb import InfluxDBClient

import pprint
_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _process_data(inData, fldNames):
    outData = []

    for row in inData:
        # Filter each row to only hold approved keys using dictionary comprehension
        outData.append({key: row[key] for key in fldNames})

    return outData


# =========================================================
#                  C S V   F U N C T I O N S
# =========================================================
def save_csv_data(data, dbFName, dbFlds):
    """Save data to CSV file.
    
    Args:
        data:    List with one or more data rows
        dbFName: CSV file name
        dbFlds:  Dict with field names (as keys) and data types

    Raises:
        OSError: If unable to access or save data to CSV file.
    """

    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
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
    
    
def save_json_data(data, dbFName, dbFlds):
    """Save data to JSON file.

    Args:
        data:    List with one or more data rows
        dbFName: JSON file name
        dbFlds:  Dict with field names (as keys) and data types

    Raises:
        OSError: If unable to access or save data to JSON file.
    """

    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
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
def _connect_sqlite(dbFName):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        dbConn = sqlite3.connect(dbFName)
        
    except sqlite3.Error as e:
        raise OSError("Failed to connect to database '{}'\n{}!".format(dbFName, e))
    
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


def save_sqlite_data(data, dbFName, tblFlds, tblName):
    """Save data to SQLite database.

    Args:
        data:     List with one or more data rows
        dbFName:  File name for SQLite database
        tblFlds:  Dict w DB field names and data types
        tblName:  DB table name

    Returns:
        int:      Last row ID
    """

    dbConn = _connect_sqlite(dbFName)
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


def get_sqlite_data(dbFName, tblFlds, tblName, orderBy, numRecs=1, first=True):
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

    def _create_orderby_param(inStr):
        parts = inStr.split('|')
        
        if len(parts) == 1:
            return 'ORDER BY {}'.format(parts[0])
        elif len(parts) >= 2:
            return 'ORDER BY {} {}'.format(parts[0], parts[1].upper())
        else:    
            return ''
    
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()
    
    fldNames = tblFlds.keys()
    dbCur.execute("SELECT {} FROM {} {} LIMIT {}".format(
        ','.join("{!s}".format(key) for key in fldNames),
        tblName, 
        _create_orderby_param(list(fldNames)[0] if orderBy is None else orderBy), 
        numRecs)
    )
    
    dataRecords = dbCur.fetchall()
    dbConn.close()

    data = []
    for row in dataRecords:
        # Create dictionary with keys from field name 
        # list, mapped against vaues from database.
        data.append(dict(zip(tblFlds.keys(), row)))

    return data

    
# =========================================================
#             I N F L U X   F U N C T I O N S
# =========================================================
def _connect_influx(db):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        dbConn = sqlite3.connect(dbFName)
        
    except sqlite3.Error as e:
        raise OSError("Failed to connect to database '{}'\n{}!".format(dbFName, e))
    
    return dbConn


def _exist_influx_table(dbCur, tblName):
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


def save_influx_data(data, dbhost, dbport, dbuser, dbpswd, tblFlds, fldTypes, tblName):
    dbClient = _connect_influx(dbhost, dbport, dbuser, dbpswd)
    
    #if not _exist_sqlite_table(dbCur, tblName):
    #    _create_sqlite_table(dbCur, tblName, dict(zip(tblFlds, fldTypes)))
    #else:
    #    for row in data:
    #        _save_sqlite_data_row(dbCur, tblName, tblFlds, row)

    #dbConn.commit()
    #dbConn.close()
    print(data)
    print(tblFlds)
    print(fldTypes)
    print(tblName)
    print('-- SAVING TO INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    
    
def get_influx_data(db, dbuser, dbpswd, numRecs=1, first=True):
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()

    #dataRecords = _get_sqlite_data_rows(dbCur, tblName, tblFlds, orderBy, numRecs, first)
    #dbConn.close()

    data = []
    for row in dataRecords:
        # This creates a dictionary with keys from field name list, mapped against vaues from database.
        data.append(dict(zip(tblFlds, row)))

    return data
    print(numRecs)
    print(first)
    print('-- RETRIEVING FROM INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    return []
