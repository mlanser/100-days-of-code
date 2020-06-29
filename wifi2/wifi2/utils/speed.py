import sys
import os
import re
import subprocess
import time
import click
import json
import sqlite3




# =========================================================
#                  C S V   F U N C T I O N S
# =========================================================
def save_csv_data(dbFName, data):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        dbFile = open(dbFName, 'a+')
        if os.stat(dbFName).st_size == 0:
            dbFile.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')
        
        for row in data:
            dbFile.write('{},{},{},{},{}\r\n'.format(
                time.strftime('%m/%d/%y', time.localtime(row['time'])),
                time.strftime('%H:%M', time.localtime(row['time'])),
                row['ping'],
                row['download'],
                row['upload']))

    except:
        raise click.ClickException("Failed to save data to '{}'!".format(dbFName))
        
    finally:
        dbFile.close()
    

def get_csv_data(dbFName, count = 1):
    try:
        dbFile = open(dbFName, 'r')
        headers = dbFile.readline()
        print(type(headers))
        print(headers)

    except:
        raise click.ClickException("Failed to save data to '{}'!".format(dbFName))

    finally:
        dbFile.close()

    
# =========================================================
#                 J S O N   F U N C T I O N S
# =========================================================
def _read_json(dbFName):
    try:
        dbFile = open(dbFName, "r")
        data = json.load(dbFile)
        
    except json.JSONDecodeError:
        return None             # We'll just 'overwrite' the file if it's empty 
                                # or if we can't read it.
    finally:
        dbFile.close()
        
    return data    

        
def _write_json(dbFName, data):
    try:
        dbFile = open(dbFName, "w")
        json.dump(data, dbFile)
        
    except:
        raise click.ClickException("Failed to write data to '{}'!".format(dbFName))
        
    finally:
        dbFile.close()
    
    
def save_json_data(dbFName, data):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    jsonData = _read_json(dbFName) if os.path.exists(dbFName) else None
    
    _write_json(dbFName, data if jsonData == None else jsonData + data)

    
def get_json_data(dbFName, count = 1):
    pass



    
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
        raise click.ClickException("Failed to connect to database '{}' [Error: {}]!".format(dbFName, e))
    
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


def get_sqlite_data(dbFName, count = 1):
    pass

    
# =========================================================
#             I N F L U X   F U N C T I O N S
# =========================================================
def save_influx_data(db, dbuser, dbpswd, data):
    print('-- SAVING TO INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    
    
def get_influx_data(db, dbuser, dbpswd, count = 1):
    pass

    
# =========================================================
#          S P E E D T E S T   F U N C T I O N S
# =========================================================
def run_speed_test(settings):
    try:
        proc = subprocess.Popen('speedtest-cli --simple',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        
    except OSError as e:
        raise click.ClickException("Failed to run 'speedtest-cli' utility! [Orig: {}]".format(e))

    proc.wait() 
    if proc.returncode != 0:
        raise click.ClickException("Failed to run and/or missing 'speedtest-cli' utility! [Code: {}]".format(str(proc.returncode)))
        
    response = proc.stdout.read()
    
    timeStamp = time.time()
    ping = re.findall('Ping:\s(.*?)\s', str(response), re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', str(response), re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', str(response), re.MULTILINE)

    return {
        'time': timeStamp,
        'ping': ping[0].replace(',', '.'),
        'download': download[0].replace(',', '.'),
        'upload': upload[0].replace(',', '.'),
    }


def save_speed_data(settings, data):
    if settings['data']['storage'].lower() == 'csv':
        save_csv_data(settings['data']['db'], data)
        
    elif settings['data']['storage'].lower() == 'json':
        save_json_data(settings['data']['db'], data)
        
    elif settings['data']['storage'].lower() == 'sqlite':
        save_sqlite_data(settings['data']['db'], data)
        
    elif settings['data']['storage'] == 'Influx':
        save_influx_data(settings['data']['db'], settings['data']['dbuser'], settings['data']['dbpswd'], data)
        
    else:    
        raise click.ClickException("Data storage type '{}' is not supported!".format(str(settings['data']['storage'])))

        
def get_speed_data(settings, count):
    if settings['data']['storage'].lower() == 'csv':
        get_csv_data(settings['data']['db'], count)
        
    elif settings['data']['storage'].lower() == 'json':
        get_json_data(settings['data']['db'], count)
        
    elif settings['data']['storage'].lower() == 'sqlite':
        get_sqlite_data(settings['data']['db'], count)
        
    elif settings['data']['storage'] == 'Influx':
        get_influx_data(settings['data']['db'], settings['data']['dbuser'], settings['data']['dbpswd'], count)
        
    else:    
        raise click.ClickException("Data storage type '{}' is not supported!".format(str(settings['data']['storage'])))
