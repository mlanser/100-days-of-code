import os
import json

#import pprint
#_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _process_data(dataIn, fldNames):
    dataOut = []

    for row in dataIn:
        # Filter each row to only hold approved keys using dictionary comprehension
        dataOut.append({key: row[key] for key in fldNames})

    return dataOut


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
    
    
# =========================================================
#            S A V E   D A T A   F U N C T I O N S
# =========================================================
def save_data(data, dbFName, dbFlds, force=True):
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
            try:
                path = os.path.dirname(os.path.abspath(dbFName))
                if not os.path.exists(path):
                    os.makedirs(path)

            except OSError as e:
                raise OSError("Failed to create path '{}'!\n{}".format(path, e))
        else:
            raise OSError("JSON data file '{}' does not exist!".format(dbFName))
            
    try:
        oldData = _read_json(dbFName) if os.path.exists(dbFName) else None
        newData = _process_data(data, dbFlds.keys())

        _write_json(dbFName, newData if oldData is None else oldData + newData)

    except OSError as e:
        raise OSError("Failed to access '{}'!\n{}".format(dbFName, e))


# =========================================================
#            G E T   D A T A   F U N C T I O N S
# =========================================================
def get_data(dbFName, dbFlds, numRecs=1, first=True):
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
