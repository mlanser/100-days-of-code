import os
import csv

#import pprint
#_PP_ = pprint.PrettyPrinter(indent=4)


# =========================================================
#             G E N E R I C   F U N C T I O N S
# =========================================================
def _row_counter(fp):
    for cntr, row in enumerate(fp, 0):  # Count all lines/rows ...
        pass
    fp.seek(0)                          # ... and 'rewind' file to beginning

    return cntr


def _process_row(rowIn, flds):
    rowOut = {}
    for key, val in rowIn.items():
        if key in flds:
            rowOut.update({key : flds[key](val)})

    return rowOut


# =========================================================
#            S A V E   D A T A   F U N C T I O N S
# =========================================================
def save_data(data, dbFName, dbFlds, force=True):
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
            try:
                path = os.path.dirname(os.path.abspath(dbFName))
                if not os.path.exists(path):
                    os.makedirs(path)

            except OSError as e:
                raise OSError("Failed to create path '{}'!\n{}".format(path, e))
                
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
    

# =========================================================
#            G E T   D A T A   F U N C T I O N S
# =========================================================
def get_data(dbFName, dbFlds, numRecs=1, first=True):
    """Retrieve data from CSV file.
    
    Args:
        dbFName:  CSV file name
        dbFlds:   Dict with field names (as keys) and data types
        numRecs:  Number of records to retrieve
        first:    If TRUE, retrieve first 'numRecs' records. Else retrieve last 'numRecs' records.

    Raises:
        OSError: If unable to access or read data from CSV file.
    """

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
