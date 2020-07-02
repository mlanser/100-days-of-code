import requests
import os
import re
import click
import time
#import png

from pathlib import Path
from .utils.settings import read_settings, save_settings, show_settings, isvalid_settings
from .utils.qr import wifi_qr
from .utils.speedtest import run_speed_test, get_speed_data, save_speed_data

APP_NAME = 'wifi2'
APP_CONFIG = 'config.ini'
APP_MAX_RUNS = 100
APP_SLEEP = 60


# =========================================================
#                H E L P E R   C L A S S E S
# =========================================================
class ApiKey(click.ParamType):
    name = 'api-key'
    
    def convert(self, value, param, ctx):
        found = re.match(r'[0-9a-f]{32}', value)

        if not found:
            self.fail(
                f'{value} is not a 32-character hexadecimal string',
                param,
                ctx,
            )

        return value


# =========================================================
#              H E L P E R   F U N C T I O N S
# =========================================================
def _data_formatter(data):
    return (
        time.strftime('%m/%d/%y %H:%M', time.localtime(data['time'])), 
        data['ping'],
        data['download'],
        data['upload']
    )


def current_weather(location, api_key='OWM_API_KEY'):
    """-- DUMMY FUNCTION --
    
    Args:
        location:  blah
        api_key:   blah
    """
    url = 'https://api.openweathermap.org/data/2.5/weather'

    query_params = {
        'q': location,
        'appid': api_key,
    }

    response = requests.get(url, params=query_params)

    return response.json()['weather'][0]['description']


def show_speed_data(data, raw=False):
    """Format and display SpeedTest data.
    
    Args:
        data: Individual data row/record as list.
        raw:  If TRUE, data is is 'raw' format.
    """
    template = "DATE: {}\nPING: {} ms\nDOWN: {} Mbit/s\nUP:   {} Mbit/s"
    # @todo validate that we have enough data points in list
    click.echo(template.format(*_data_formatter(data)) if raw else template.format(' '.join((data[0], data[1])), data[2], data[3], data[4]))
        

def show_speed_data_table(data, raw=False):
    """Format and display SpeedTest data.
    
    Args:
        data: List of data rows/records if 'table' is TRUE. Else use individual data row/record.
        raw:  If TRUE, data is is 'raw' format.
    """
    
    template = " {!s:18s} | {:8.3f} | {:8.2f} | {:8.2f} " if raw else " {:18s} | {:8s} | {:8s} | {:8s} "
    
    
    click.echo()
    #          |12345678901234567890|1234567890|1234567890|1234567890|
    #          |                    |          |          |          |
    click.echo("      Date/Time     |   PING   |   DOWN   |    UP    ")
    click.echo("--------------------|----------|----------|----------")
    click.echo("   MM/DD/YY HH:MM   |    ms    |  MBit/s  |  MBit/s  ")
    click.echo("--------------------|----------|----------|----------")
    for row in data:
        #click.echo(" {!s:18s} | {:8.3f} | {:8.2f} |  {:8.2f} ".format(*_formatter(row)))
        #click.echo(" {:18s} | {:8s} | {:8s} |  {:8s} ".format(' '.join(row[0], row[1]), row[2], row[3], row[4])
        click.echo(template.format(*_data_formatter(row)) if raw else template.format(' '.join((row[0], row[1])), row[2], row[3], row[4]))

    click.echo()

    
# =========================================================
#                C L I C K   C O M M A N D S
# =========================================================
#                  M A I N   C o m m a n d
# ---------------------------------------------------------
@click.group()
@click.option(
    '--config',
    type=click.Path(),
    default=os.path.join(click.get_app_dir(APP_NAME), APP_CONFIG),
    help='Name of config file to use.',
)
@click.pass_context
def main(ctx, config: str = ''):
    """
    This tool can check and log the current internet speed of the WiFi network. It can
    also display WiFi access credentials in text and as a QR code.
    
    To continuously check and log internet speed, simply use cron (or similar) to run
    the 'wifi2 speedtest' command on a regular basis.
    """
    ctx.obj = {
        'globals': {
            'appName': APP_NAME,
            'configFName': os.path.expanduser(config),
        }
    }
    
        
# ---------------------------------------------------------
#                   S u b - C o m m a n d s
# ---------------------------------------------------------
# CMD: configure
# ---------------------------------------------------------
@main.command()
@click.option(
    '--section',
    type=click.Choice(['wifi', 'data', 'test', 'all'], case_sensitive=False),
    default='all', show_default=True,
    help='Config file section name.',
)
@click.option(
    '--set/--show', 'update',
    default=True,
    help='Set and (save) application settings for a given section, or just show/display current settings.',
)
@click.pass_context
def configure(ctx, section: str, update: bool):
    """
    Define and store configuration values for a given section in the config file.
    """
    if not section.lower() in ['wifi', 'data', 'test', 'all']:
        raise click.BadParameter("Invalid section '{}'".format(section))

    if update:
        save_settings(ctx.obj['globals'], section.lower())
    else:
        show_settings(ctx.obj['globals'], section.lower())


# ---------------------------------------------------------
# CMD: creds
# ---------------------------------------------------------
@main.command()
@click.option(
    '--how',
    type=click.Choice(['terminal', 'png'], case_sensitive=False),
    default='terminal', show_default=True,
    help='Display QR code with WiFi creds in terminal or save to file.',
)
@click.option(
    '-f', '--fname', 'filename', 
    type=click.Path(),
    default='',
    help='Full path to PNG file')
@click.pass_context
def creds(ctx, how: str, filename: str = ''):
    """
    Show QR code for WiFi credentials.
    """
    ctx.obj['settings'] = read_settings(ctx.obj['globals'])
    if not isvalid_settings(ctx.obj['settings']):
        raise click.ClickException("Invalid and/or incomplete config info!")

    qr = wifi_qr(
        ctx.obj['settings']['wifi']['ssid'], 
        ctx.obj['settings']['wifi']['security'], 
        ctx.obj['settings']['wifi']['password']
    )
        
    if how.lower() == 'terminal':
        click.echo(qr.terminal())
    else:
        cleanFName = filename.strip().replace(' ', '-')
        if not cleanFName:
            cleanFName = '{}/{}-QR.png'.format(Path.home(), str(ctx.obj['settings']['wifi']['ssid']).upper().replace(' ', '-'))
            
        path = os.path.dirname(os.path.abspath(cleanFName))
        if not os.path.exists(path):
            os.makedirs(path)
        
        try:
            qr.png(filename, scale=10)
        except OSError as e:
            raise click.ClickException("Unable to save PNG file! [Error: {}]".format(e))
            
        click.echo("Saved QR code to '{}'".format(filename))
    
    
# ---------------------------------------------------------
# CMD: speedtest
# ---------------------------------------------------------
@main.command()
@click.option(
    '--display',
    type=click.Choice(['stdout', 'epaper', 'none'], case_sensitive=False),
    default='stdout', show_default=True,
    help='Display speed test data on STDOUT or ePaper screen.',
)
@click.option(
    '--save/--no-save',
    default=True,
    help='Save speed test data to data storage.',
)
@click.option(
    '--count', 'numRun',
    type=click.IntRange(1, APP_MAX_RUNS, clamp=True),
    default=1, show_default=True,
    help='Number (1-100) of tests to run in sequence.',
)
@click.option(
    '--history',
    is_flag=True,
    help="Show history of 'all' or given number (using 'count') of previously saved speed tests.",
)
@click.pass_context
def speedtest(ctx, display: str, save: bool, history: bool, numRun: int):
    """
    Get speed test data.
    """
    
    def _csv_data_header():
        return 'Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n'
    
    def _csv_data_formatter(dataRow):
        return '{},{},{},{},{}\r\n'.format(
                time.strftime('%m/%d/%y', time.localtime(dataRow['time'])),
                time.strftime('%H:%M', time.localtime(dataRow['time'])),
                dataRow['ping'],
                dataRow['download'],
                dataRow['upload'])
    
    ctx.obj['settings'] = read_settings(ctx.obj['globals'])
    if not isvalid_settings(ctx.obj['settings']):
        raise click.ClickException("Invalid and/or incomplete config info!")

    # Only show historic data    
    if history:
        try:
            show_speed_data_table(get_speed_data(ctx.obj['settings']['data'], numRun), raw=False)
            
        except OSError as e:     
            raise click.ClickException(e)

    # Collect new data
    else:
        data = []

        for i in range(0, numRun):
            try:
                data.append(run_speed_test(ctx.obj['settings']['speedtest']))
            
            except OSError as e:     
                raise click.ClickException(e)

            if display.lower() == 'stdout':
                click.echo('-- Internet Speed Test {} of {} --'.format(str(i + 1), str(numRun)))
                show_speed_data(data[i], raw=True)

            elif display.lower() == 'epaper':
                #
                #
                click.echo('-- PRINT TO EPAPER CODE HERE --')
                #
                #

            if (i + 1) < numRun:
                time.sleep(APP_SLEEP)

        if save:
            try:
                if ctx.obj['settings']['data']['storage'].lower() == 'csv':
                    save_speed_data(ctx.obj['settings']['data'], data, _csv_data_formatter, _csv_data_header)
                else:    
                    save_speed_data(ctx.obj['settings']['data'], data)
                
            except OSError as e:     
                raise click.ClickException(e)

                
# ---------------------------------------------------------
# CMD: debug
# ---------------------------------------------------------
@main.command()
@click.option(
    '--msg',
    default='Testing 1-2-3', show_default=True,
    help='Display speed test data on STDOUT or ePaper screen.',
)
@click.pass_context
def debug(ctx, msg: str):
    """
    Show debug message.
    """
    click.echo(msg)
    click.echo("\n----------------------------------------------------")
    click.echo("App Configuration:\n{}\n".format(ctx.obj['globals']['configFName']))
    
    
# =========================================================
#              A P P   S T A R T   S E C T I O N
# =========================================================
def start():
    main(obj={})


if __name__ == '__main__':
    start()
