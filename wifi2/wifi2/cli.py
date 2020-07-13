import requests
import os
import re
import click
import time
import dateutil
import pytz

from pathlib import Path
from .utils.settings import read_settings, save_settings, show_settings, isvalid_settings
from .utils.qr import wifi_qr
from .utils.speedtest import run_speedtest, get_speed_data, save_speed_data

APP_NAME = 'wifi2'
APP_CONFIG = 'config.ini'
APP_MIN_RUNS = 1
APP_MAX_RUNS = 100
APP_HISTORY = 1000
APP_SLEEP = 60
APP_BITS = 'bits'

import pprint
_PP_ = pprint.PrettyPrinter(indent=4)


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


def _data_formatter(data, rowNum=0, isRaw=False, rateUnit=APP_BITS):
    
    def _date_maker(timestamp, timezone=None, fmtstr=None):
        dateOrig = dateutil.parser.isoparse(timestamp)
        dateFinal = dateOrig if timezone is None else dateOrig.astimezone(pytz.timezone(timezone)) 
        
        return dateFinal.strftime('%m/%d/%y %H:%M' if fmtstr is None else fmtstr)
    
    na = '- n/a -'
    out = (str(rowNum),) if rowNum > 0 else tuple()

    # Mbit/s or MB/s
    rateUnitDivisor = 1000000 if rateUnit.lower() != 'bytes' else 8000000
    
    if isRaw:
        return out + (
            na if 'timestamp' not in data else _date_maker(data['timestamp'], None, '%m/%d/%y %H:%M'),
            na if 'timestamp' not in data else _date_maker(data['timestamp'], data['locationTZ'], '%m/%d/%y %H:%M'),
            na if 'ping' not in data else float(data['ping']),
            na if 'download' not in data else float(data['download']/rateUnitDivisor),
            na if 'upload' not in data else float(data['upload']/rateUnitDivisor)
        )
    else:
        return out + (
            na if len(data) < 1 else data[0],
            na if len(data) < 2 else data[1],
            na if len(data) < 3 else data[2],
            na if len(data) < 4 else data[3],
            na if len(data) < 5 else data[4],
        )


def show_speed_data(data, isRaw=False, rateUnit=APP_BITS):
    """Format and display SpeedTest data.
    
    Args:
        data:     Individual data row/record as list.
        isRaw:    If TRUE, data is is 'raw' format.
        rateUnit: MB/s if 'bytes', else Mbit/s
    """

    # Mbit/s or MB/s
    rateUnitLabel = 'Mbit/s' if rateUnit.lower() != 'bytes' else 'MB/s'
    
    template = "DATE:     {} (UTC)\n          {} (local)\n\n"
    if isRaw:
        template += "PING: {:8.3f} ms\nDOWN: {:8.2f} " + rateUnitLabel + "\nUP:   {:8.2f} " + rateUnitLabel
    else:
        template += "PING: {:8s} ms\nDOWN: {:8s} "     + rateUnitLabel + "\nUP:   {:8s} "   + rateUnitLabel
        
    click.echo(template.format(*_data_formatter(data, 0, isRaw, rateUnit)))
    click.echo()
        

def show_speed_data_table(data, showRowNum=True, isRaw=False, rateUnit=APP_BITS):
    """Format and display SpeedTest data.
    
    Args:
        data:       List of data rows/records if 'table' is TRUE. Else use individual data row/record.
        showRowNum: If TRUE, show row number in left-most column
        isRaw:      If TRUE, data is is 'raw' format.
        rateUnit:   MB/s if 'bytes', else Mbit/s
    """
    
    # Mbit/s or MB/s
    rateUnitLabel = 'Mbit/s' if rateUnit.lower() != 'bytes' else 'MB/s'

    if showRowNum:
        #           |12345|123456789123456789|123456789123456789|1234567890|1234567890|1234567890|
        #           |     |                  |                  |          |          |          |
        hdr1      = "     |              Date/Time              |          |          |          "
        hdr2      = "     |        UTC       |   At Location    |   PING   |   DOWN   |    UP    "
        hdr3      = "  #  |  MM/DD/YY HH:MM  |  MM/DD/YY HH:MM  |    ms    |  {0:6s}  |  {0:6s}  ".format(rateUnitLabel)
        divider   = "-----|------------------|------------------|----------|----------|----------"
        
        col1 = " {:>3s} |  {!s:14s}  |  {!s:14s}  |" if isRaw else " {:>3s} |  {:14s}  |  {:14s}  |"
    else:
        #           |123456789012345678|123456789012345678|1234567890|1234567890|1234567890|
        #           |                  |                  |          |          |          |
        hdr1      = "              Date/Time              |          |          |          "
        hdr2      = "        UTC       |    At Location   |   PING   |   DOWN   |    UP    "
        hdr3      = "  MM/DD/YY HH:MM  |  MM/DD/YY HH:MM  |    ms    |  {0:6s}  |  {0:6s}  ".format(rateUnitLabel)
        divider   = "------------------|------------------|----------|----------|----------"
        
        col1 = "  {!s:14s}  |  {!s:14s}  |" if isRaw else "  {:14s}  |  {:14s}  |"

    colN = " {:8.3f} | {:8.2f} | {:8.2f} " if isRaw else " {:8s} | {:8s} | {:8s} "

    template = col1 + colN
    rowNum = 0

    click.echo()
    click.echo(hdr1)
    click.echo(hdr2)
    click.echo(divider)
    click.echo(hdr3)
    click.echo(divider)

    for row in data:
        if showRowNum:
            rowNum += 1
        click.echo(template.format(*_data_formatter(row, rowNum, isRaw, rateUnit)))

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
    """Check and log internet speed and related metrics for current connection.

    This tool can check and log the current internet speed of the WiFi network. It can
    also display WiFi access credentials in text and as a QR code.
    
    To continuously check and log internet speed, simply use cron (or similar) to run
    the 'wifi2 speedtest' command on a regular basis.
    """
    ctx.obj = {
        'globals': {
            'appName': APP_NAME,
            'configFName': os.path.expanduser(config),
            'appMinRuns': APP_MIN_RUNS,
            'appMaxRuns': APP_MAX_RUNS,
            'appHistory': APP_HISTORY,
            'appSleep': APP_SLEEP,
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
    '--count', 'cntr',
    default=1, show_default=True,
    help='Number of tests to run in sequence, or records to retrieve for review.',
)
@click.option(
    '--history',
    is_flag=True,
    help="Show history of given number (using 'count') of previously saved speed tests.",
)
@click.option(
    '--first/--last', 'first',
    default=True,
    help="Show 'first' or 'last' 'count' number of previously saved speed tests.",
)
@click.pass_context
def speedtest(ctx, display: str, save: bool, cntr: int, history: bool, first: bool):
    """Get speed test data.

    \b
    Speed data samples are retrieved/stored as follows:
        'time'      Unix timestamp
        'ping'      Ping response time (ms)
        'download'  Download speed (Mbit/s)
        'upload'    Upload speed (Mbit/s)
    """
    ctx.obj['settings'] = read_settings(ctx.obj['globals'])
    if not isvalid_settings(ctx.obj['settings']):
        raise click.ClickException("Invalid and/or incomplete config info!")

    unit = ctx.obj['settings']['speedtest'].get('unit', APP_BITS)
    
    # Show historic data
    if history:
        if cntr < 1 or cntr > ctx.obj['globals']['appHistory']:
            count = click.prompt(
                "Enter number of data records to retrieve:",
                type=click.IntRange(1, ctx.obj['globals']['appHistory'], clamp=True),
                default=1,
                show_default=True,
            )
            
        try:
            data = get_speed_data(ctx.obj['settings']['speedtest'], cntr, first)

            if len(data):
                show_speed_data_table(data, showRowNum=True, isRaw=True, rateUnit=unit)
            else:
                click.echo('-- No data records found! --')

        except OSError as e:     
            raise click.ClickException(e)

    # Collect new data
    else:
        if cntr <  ctx.obj['globals']['appMinRuns'] or cntr > ctx.obj['globals']['appMaxRuns']:
            count = click.prompt(
                "Enter number of test cycle runs:",
                type=click.IntRange(ctx.obj['globals']['appMinRuns'], ctx.obj['globals']['appMaxRuns'], clamp=True),
                default=ctx.obj['globals']['appMinRuns'],
                show_default=True,
            )

        data = []
        for i in range(0, cntr):
            try:
                data.append(run_speedtest(ctx.obj['settings']['speedtest']))
            
            except OSError as e:     
                raise click.ClickException(e)

            if display.lower() == 'stdout':
                click.echo('-- Internet Speed Test {} of {} --'.format(str(i + 1), str(cntr)))
                show_speed_data(data[i], isRaw=True, rateUnit=unit)

            elif display.lower() == 'epaper':
                #
                #
                click.echo('-- PRINT TO EPAPER CODE HERE --')
                #
                #

            if (i + 1) < cntr:
                time.sleep(APP_SLEEP)

        if save:
            try:
                save_speed_data(ctx.obj['settings']['speedtest'], data)

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
