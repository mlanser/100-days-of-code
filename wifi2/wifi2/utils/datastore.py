import os
import json
import sqlite3
from influxdb import InfluxDBClient

# import pprint
# _PP_ = pprint.PrettyPrinter(indent=4)


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
def _count_csv_recs(dbFName):
    """Count number of records/rows in CSV file

    Args:
        dbFName: CSV file name

    Returns:
         Number or records.

         Please note that the first row in the file is supposed
         to be the header row. So if the file is empty or has
         only 1 row - the header row - then the file has no records.
    """

    try:
        dbFile = open(dbFName, 'r')

    except OSError as e:
        raise OSError("Failed to read '{}'! -- {}".format(dbFName, e))

    else:
        with dbFile:
            for cntr, row in enumerate(dbFile, 0):
                pass
        dbFile.close()

    return cntr


def save_csv_data(data, dbFName, dbFlds):
    """Save data to CSV file.
    
    Args:
        data:    List with one or more data rows
        dbFName: CSV file name
        dbFlds:  List of field names

    Raises:
        OSError: If unable to access or save data to CSV file.
    """
    def _header_row(listFlds):
        return '{}\r\n'.format(','.join(listFlds))

    def _data_row_formatter(dataRow, listFlds):
        # Using list comprehension to only pull exactly what we want/need
        return '{}\r\n'.format(','.join(str(dataRow[key]) for key in listFlds))

    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        dbFile = open(dbFName, 'a+')

    except OSError as e:
        raise OSError("Failed to save data to '{}'! - {}".format(dbFName, e))

    else:
        if os.stat(dbFName).st_size == 0:
            dbFile.write(_header_row(dbFlds))

        for row in data:
            dbFile.write(_data_row_formatter(row, dbFlds))

        dbFile.close()
    

def get_csv_data(dbFName, dbFlds, numRecs=1, first=True):
    """Retrieve data from CSV file.
    
    Args:
        dbFName:  CSV file name
        dbFlds:   List of data record field names
        numRecs:  Number of records to retrieve
        first:    If TRUE, retrieve first 'numRecs' records. Else retrieve last 'numRecs' records.

    Raises:
        OSError: If unable to access or read data from CSV file.
    """

    try:
        dbFile = open(dbFName, 'r')
        raw = dbFile.readline().rstrip('\n')    # Read header row
        if not raw:
            raise OSError("Empty data file")

        data = []
        lastRec = numRecs if first else _count_csv_recs(dbFName)
        firstRec = 0 if first else max(0, lastRec - numRecs)

        for i in range(0, lastRec):             # Read data records
            raw = dbFile.readline().rstrip('\n')
            if i < firstRec:
                continue
            elif raw:
                data.append(dict(zip(dbFlds, raw.split(','))))
            else:
                break

    except OSError as e:
        raise OSError("Failed to read data from '{}'! -- {}".format(dbFName, e))

    else:
        dbFile.close()
        
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
        raise OSError("Failed to write data to '{}'! -- {}".format(dbFName, e))
        
    else:
        dbFile.close()
    
    
def save_json_data(data, dbFName, dbFlds):
    """Save data to JSON file.

    Args:
        data:    List with one or more data rows
        dbFName: CSV file name
        dbFlds:  List of field names

    Raises:
        OSError: If unable to access or save data to CSV file.
    """

    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    try:
        oldData = _read_json(dbFName) if os.path.exists(dbFName) else None
        newData = _process_data(data, dbFlds)

        _write_json(dbFName, newData if oldData is None else oldData + newData)

    except OSError as e:
        raise OSError("Failed to access '{}'! [Error {}]".format(dbFName, e))


def get_json_data(dbFName, dbFlds, numRecs=1, first=True):
    """Retrieve data from JSON file.

    Args:
        dbFName: JSON file name
        dbFlds:  List of field names
        numRecs: Number of records to retrieve
        first:   If TRUE, retrieve first 'numRecs' records. Else retrieve last 'numRecs' records.

    Raises:
        OSError: If unable to access or read data from CSV file.
    """

    try:
        jsonData = _read_json(dbFName) if os.path.exists(dbFName) else None

        if jsonData is None:
            data = []
        else:
            lastRec = numRecs if first else len(jsonData)
            firstRec = 0 if first else max(0, lastRec - numRecs)
            data = _process_data(jsonData[firstRec:lastRec], dbFlds)

    except OSError as e:
        raise OSError("Failed to read data from '{}'! [Error: {}]".format(dbFName, e))

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
        raise OSError("Failed to connect to database '{}' [Error: {}]!".format(dbFName, e))
    
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


def _save_sqlite_data_row(dbCur, tblName, fldNames, dataRow):
    """Save single row of data to the database.

    Args:
        dbCur:    DB cursor for a given database connection
        tblName:  Table name to look for
        fldNames: Field names used in table
        dataRow:  Dictionary with field names (as keys) and associated data values

    Returns:
        int:      Last row ID
    """

    flds = ','.join(fldNames)
    vals = ','.join("?" for (_) in fldNames)

    # Using list comprehension to only pull values that we want/need from data row
    dbCur.execute("INSERT INTO {}({}) VALUES({})".format(tblName, flds, vals),
                  [dataRow[key] for key in fldNames])
    
    return dbCur.lastrowid


def _get_sqlite_data_rows(dbCur, tblName, fldNames, orderBy=None, numRecs=1, first=True):
    """Retrieve 'numrec' data records from database.

    Args:
        dbCur:    DB cursor for a given database connection
        tblName:  Table name to look for
        fldNames: Field names used in table
        orderBy:  Field to be sorted by
        numRecs:  Number of records to retrieve
        first:    If TRUE, rerieve first 'numRec' records, else retrieve last 'numRec' records.

    Returns:
        list:     List of all records retrieved
    """

    flds = ','.join("{!s}".format(key) for key in fldNames)
    sort = (fldNames[0] if orderBy is None else orderBy) + ('' if first else ' DESC')
    dbCur.execute("SELECT {} FROM {} ORDER BY {} LIMIT {}".format(flds, tblName, sort, numRecs))

    return dbCur.fetchall()


def save_sqlite_data(data, dbFName, tblFlds, fldTypes, tblName):
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()

    if not _exist_sqlite_table(dbCur, tblName):
        _create_sqlite_table(dbCur, tblName, dict(zip(tblFlds, fldTypes)))
    else:
        for row in data:
            _save_sqlite_data_row(dbCur, tblName, tblFlds, row)

    dbConn.commit()
    dbConn.close()


def get_sqlite_data(dbFName, tblFlds, orderBy, tblName, numRecs=1, first=True):
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()

    dataRecords = _get_sqlite_data_rows(dbCur, tblName, tblFlds, orderBy, numRecs, first)
    dbConn.close()

    data = []
    for row in dataRecords:
        # This creates a dictionary with keys from field name list, mapped against vaues from database.
        data.append(dict(zip(tblFlds, row)))

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
        raise OSError("Failed to connect to database '{}' [Error: {}]!".format(dbFName, e))
    
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

    dataRecords = _get_sqlite_data_rows(dbCur, tblName, tblFlds, orderBy, numRecs, first)
    dbConn.close()

    data = []
    for row in dataRecords:
        # This creates a dictionary with keys from field name list, mapped against vaues from database.
        data.append(dict(zip(tblFlds, row)))

    return data
    print(numRecs)
    print(first)
    print('-- RETRIEVING FROM INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    return []
