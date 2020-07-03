#import sys
#import re
#import time
#import click
import os
import json
import sqlite3


# =========================================================
#                  C S V   F U N C T I O N S
# =========================================================
def save_csv_data(dbFName, data, csvFmt=None, csvHdr=None):
    """Save data to CSV file.
    
    Args:
        dbFName: CSV file name
        data:    List with one or more data rows
        csvFmt:  CSV row formatter callback function (which must return a string)
        csvHdr:  CSV header row string. If blank (i.e. "None"), then no header line will be created.
        
    Raises:
        OSError: If unable to access or save data to CSV file.
    """
    dbFile = None

    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        dbFile = open(dbFName, 'a+')
        if os.stat(dbFName).st_size == 0 and csvHdr is not None:
            dbFile.write(csvHdr())
        
        for row in data:
            dbFile.write(csvFmt(row))

    except OSError as e:
        raise OSError("Failed to save data to '{}'! [Error {}]".format(dbFName, e))
        
    finally:
        if dbFile is not None:
            dbFile.close()
    

def get_csv_data(dbFName, numRecs=1, skipHdr=True):
    """Retrieve data from CSV file.
    
    Args:
        dbFName: CSV file name
        numRecs: Number of records to retrieve
        skipHdr: If TRUE, assume first row is header and start reading next row as 1st data row
        
    Raises:
        OSError: If unable to access or read data from CSV file.
    """
    dbFile = None
    data = []

    try:
        dbFile = open(dbFName, 'r')
        raw = dbFile.readline().rstrip('\n')

        if not raw:
            raise OSError("Empty data file")

        if skipHdr:
            numRecs += 1
        else:    
            data.append(raw.split(','))
            
        for i in range(1, numRecs):
            raw = dbFile.readline().rstrip('\n')
            if raw:
                data.append(raw.split(','))
            else:
                break

    except OSError as e:
        raise OSError("Failed to read data from '{}'! -- {}".format(dbFName, e))

    finally:
        if dbFile is not None:
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
        return None                 #  if it's empty or if we can't read it.

    finally:
        dbFile.close()
        
    return data    

        
def _write_json(dbFName, data):
    try:
        dbFile = open(dbFName, "w")
        json.dump(data, dbFile)
        
    except OSError as e:
        raise OSError("Failed to write data to '{}'! [Error: {}]".format(dbFName, e))
        
    finally:
        dbFile.close()
    
    
def save_json_data(dbFName, data):
    """Save data to JSON file.

    Args:
        dbFName: CSV file name
        data:    List with one or more data rows

    Raises:
        OSError: If unable to access or save data to CSV file.
    """
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    try:
        jsonData = _read_json(dbFName) if os.path.exists(dbFName) else None
        _write_json(dbFName, data if jsonData is None else jsonData + data)

    except OSError as e:
        raise OSError("Failed to access '{}'! [Error {}]".format(dbFName, e))


def get_json_data(dbFName, numRecs=1):
    """Retrieve data from CSV file.

    Args:
        dbFName: JSON file name
        numRecs: Number of records to retrieve

    Raises:
        OSError: If unable to access or read data from CSV file.
    """
    try:
        jsonData = _read_json(dbFName) if os.path.exists(dbFName) else None
        print(len(jsonData))

    except OSError as e:
        raise OSError("Failed to read data from '{}'! [Error: {}]".format(dbFName, e))

    return []


# =========================================================
#               S Q L I T E   F U N C T I O N S
# =========================================================
def _connect_sqlite(dbFName):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    dbConn = None
    try:
        dbConn = sqlite3.connect(dbFName)
        
    except sqlite3.Error as e:
        raise OSError("Failed to connect to database '{}' [Error: {}]!".format(dbFName, e))
    
    return dbConn


def _create_sqlite_table(dbCur):
    dbCur.execute('''CREATE TABLE IF NOT EXISTS records (time real, ping real, download real, upload real)''')


def _save_sqlite_datarow(dbCur, dataRow):
    dbCur.execute('''INSERT INTO records(time,ping,download,upload) VALUES(?,?,?,?)''',
                  [dataRow['time'], dataRow['ping'], dataRow['download'], dataRow['upload']])
    
    return dbCur.lastrowid


def save_sqlite_data(dbFName, data):
    dbConn = _connect_sqlite(dbFName)
    dbCur = dbConn.cursor()
    
    _create_sqlite_table(dbCur)
    
    for row in data:
        dbCur = _save_sqlite_datarow(dbCur, row)
    
    dbConn.commit()
    dbConn.close()


def get_sqlite_data(dbFName, numRecs=1):
    return []

    
# =========================================================
#             I N F L U X   F U N C T I O N S
# =========================================================
def save_influx_data(db, dbuser, dbpswd, data):
    print('-- SAVING TO INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    
    
def get_influx_data(db, dbuser, dbpswd, numRecs=1):
    return []
