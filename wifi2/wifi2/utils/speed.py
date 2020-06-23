import sys
import os
import re
import subprocess
import time
import click


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
        raise click.ClickException("Missing and/or failed to run 'speedtest-cli' utility! [Code: {}]".format(str(proc.returncode)))
        
    response = proc.stdout.read()
        
    ping = re.findall('Ping:\s(.*?)\s', str(response), re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', str(response), re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', str(response), re.MULTILINE)

    return {
        'ping': ping[0].replace(',', '.'),
        'download': download[0].replace(',', '.'),
        'upload': upload[0].replace(',', '.'),
    }


def save_speed_data(settings, data):
    try:
        f = open('/home/pi/Code/Python/speedtest.csv', 'a+')
        if os.stat('/home/pi/Code/Python/speedtest.csv').st_size == 0:
            f.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')

        f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))

    except:
        pass

    finally:
        f.close()
