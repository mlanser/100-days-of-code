import os
import sqlite3

#import pprint
#_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _connect_server(dbFName, force=True):
    if not os.path.exists(dbFName):
        if force:
            try:
                path = os.path.dirname(os.path.abspath(dbFName))
                if not os.path.exists(path):
                    os.makedirs(path)

            except OSError as e:
                raise OSError("Failed to create path '{}'!\n{}".format(path, e))
                
        else:
            raise OSError("SQLite data file '{}' does not exist!".format(dbFName))
            
    try:
        dbConn = sqlite3.connect(dbFName)
        
    except sqlite3.Error as e:
        raise OSError("Failed to connect to SQLite database '{}'\n{}!".format(dbFName, e))
    
    return dbConn


def _exist_table(dbCur, tblName):
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


def _create_table(dbCur, tblName, fldNamesWithTypes):
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

    dbConn = _connect_server(dbFName, force)
    dbCur = dbConn.cursor()

    if not _exist_table(dbCur, tblName):
        _create_table(dbCur, tblName, tblFlds)
    
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
    
    dbConn = _connect_server(dbFName)
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
