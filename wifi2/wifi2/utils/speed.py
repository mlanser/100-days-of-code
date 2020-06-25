import sys
import os
import re
import subprocess
import time
import click
import json


def get_speed_data(settings):
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


def save_data_to_csv(data, dbFName):
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
    

    
def _read_json_file(dbFName):
    try:
        dbFile = open(dbFName, "r")
        data = json.load(dbFile)
        
    except json.JSONDecodeError:
        return None             # We'll just 'overwrite' the file if it's empty 
                                # or if we can't read it.
    finally:
        dbFile.close()
        
    return data    

        
def _write_json_file(dbFName, data):
    try:
        dbFile = open(dbFName, "w")
        json.dump(data, dbFile)
        
    except:
        raise click.ClickException("Failed to write data to '{}'!".format(dbFName))
        
    finally:
        dbFile.close()
    
    
def save_data_to_json(data, dbFName):
    if not os.path.exists(dbFName):
        path = os.path.dirname(os.path.abspath(dbFName))
        if not os.path.exists(path):
            os.makedirs(path)
    
    jsonData = _read_json_file(dbFName) if os.path.exists(dbFName) else None
    
    _write_json_file(dbFName, data if jsonData == None else jsonData + data)

    
def save_data_to_sql(data, db, dbuser, dbpswd):
    print('-- SAVING TO SQL -- {}:{}:{}'.format(db, dbuser, dbpswd))
    
    
def save_data_to_influx(data, db, dbuser, dbpswd):
    print('-- SAVING TO INFLUX -- {}:{}:{}'.format(db, dbuser, dbpswd))
    
    
def save_speed_data(settings, data):
    if settings['data']['storage'].upper() == 'CSV':
        save_data_to_csv(data, settings['data']['db'])
        
    elif settings['data']['storage'].upper() == 'JSON':
        save_data_to_json(data, settings['data']['db'])
        
    elif settings['data']['storage'].upper() == 'SQL':
        save_data_to_sql(data, settings['data']['db'], settings['data']['dbuser'], settings['data']['dbpswd'])
        
    elif settings['data']['storage'] == 'Influx':
        save_data_to_influx(data, settings['data']['db'], settings['data']['dbuser'], settings['data']['dbpswd'])
        
    else:    
        raise click.ClickException("Data storage type '{}' is not supported!".format(str(settings['data']['storage'])))
