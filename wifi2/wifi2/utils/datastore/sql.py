import os
import sys
import mariadb

#import pprint
#_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _connect_server(url, dbUser, dbPswd, dbName):
    urlParts = urlsplit(url)
    
    try:
        dbClient = mariadb.connect(
                        user=dbUser, 
                        password=dbPswd, 
                        host=urlParts.hostname, 
                        port=urlParts.port, 
                        database=dbName
                    )
        
    except mariadb.Error as e:
        raise OSError("Failed to connect to SQL database '{}'\n{}!".format(host, e))
    
    # We want to disable 'autocommit' feature for 
    # this database connection so that we can manually 
    # commit and rollback as needed.
    dbClient.autocommit = False         
    
    return dbClient


def _exist_table(dbCur, tblName):
    """Check if a table with a given name exists.

    Args:
        dbCur:   DB cursor for a given database connection
        tblName: Table name to look for

    Returns:
        bool:    TRUE if table exists, Else FALSE.
    """

    dbCur.execute("SHOW tables;")
    tables = dbCur.fetchall()
    print('--tables--')
    _PP_.pprint(tables)
    print('----------')
    return True
    return True if dbCur.fetchone()[0] == 1 else False


def _create_sqlite_table(dbCur, tblName, fldNamesWithTypes):
    """Create table with fields.

    Args:
        dbCur:   DB cursor for a given database connection
        tblName: Table name to look for
        fldNamesWithTypes: Dictionary with field names and associated SQLite data types
    """

    def _split_type_idx(inStr):
        parts = inStr.split('|')
        if len(parts) > 1:
            return (parts[0], True if parts[1].lower() == 'idx' else False)
        else:
            return (parts[0], False)
    
    flds = ','.join("{!s} {!s}".format(key, _split_type_idx(val)[0]) for (key, val) in fldNamesWithTypes.items())
    dbCur.execute("CREATE TABLE IF NOT EXISTS {0} ({1});".format(tblName, flds))
        
    # SQLite automatically creates a 'primary key' column and we'll therefore 
    # only create indexed columns as indicated in 'fldNamesWithTypes'.
    for (key, val) in fldNamesWithTypes.items():
        if _split_type_idx(val)[1]:
            dbCur.execute("CREATE INDEX idx_{0}_{1} ON {0}({1});".format(tblName, key))


# =========================================================
#            S A V E   D A T A   F U N C T I O N S
# =========================================================
def save_data(data, dbFName, tblFlds, tblName, force=True):
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

    if not _exist_table(dbCur, tblName):
        _create_table(dbCur, tblName, tblFlds)
    
    dbConn.close()
    
    #insert information 
    #try: 
    #    cur.execute("INSERT INTO employees (first_name,last_name) VALUES (?, ?)", ("Maria","DB")) 
    #except mariadb.Error as e: 
    #    print(f"Error: {e}")
    
    fldNames = tblFlds.keys()
    flds = ','.join(fldNames)
    vals = ','.join("?" for (_) in fldNames)
    for row in data:
        # Using list comprehension to only pull values 
        # that we want/need from a row of data
        dbCur.execute("INSERT INTO {}({}) VALUES({})".format(tblName, flds, vals),
                      [row[key] for key in fldNames])
        
    try:
        cursor.execute("some MariaDB query")
    except mariadb.Error as e:
        print(f"Error: {e}")
    
    #conn.commit() 
    #print(f"Last Inserted ID: {cur.lastrowid}")
    #conn.close()
    
    dbConn.commit()
    dbConn.close()


# =========================================================
#            G E T   D A T A   F U N C T I O N S
# =========================================================
def get_data(dbFName, tblFlds, tblName, orderBy=None, numRecs=1, first=True):
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

    #retrieving information 
    #some_name = "Georgi" 
    #cur.execute("SELECT first_name,last_name FROM employees WHERE first_name=?", (some_name,)) 

    #for first_name, last_name in cur: 
    #    print(f"First name: {first_name}, Last name: {last_name}")    
    
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
