import requests
import os
import re
import click
import time
import png

from pathlib import Path
from .utils.settings import read_settings, save_settings, show_settings, isvalid_settings
from .utils.qr import wifi_qr
from .utils.speed import get_speed_data, save_speed_data

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
def current_weather(location, api_key='OWM_API_KEY'):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    query_params = {
        'q': location,
        'appid': api_key,
    }

    response = requests.get(url, params=query_params)

    return response.json()['weather'][0]['description']




# =========================================================
#                C L I C K   C O M M A N D S
# =========================================================
#                  M A I N   C o m m a n d
# ---------------------------------------------------------
@click.group()
@click.option(
    '--config',
    type = click.Path(),
    default = os.path.join(click.get_app_dir(APP_NAME), APP_CONFIG),
    help = 'Name of config file to use.',
)
@click.pass_context
def main(ctx, config: str = ''):
    """
    This tool can check and log the current internet speed of the WiFi network. It can also display WiFi access credentials in text and as a QR code.
    
    To continuously check and log internet speed, simply use cron (or similar) to run the 'wifi2 speedtest' command on a regular basis.
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
    type = click.Choice(['wifi', 'data', 'speedtest', 'all'], case_sensitive=False),
    default = '',
    help = 'Config file section name.',
)
@click.option(
    '--set/--show',
    default = True,
    help = 'Set (and (save) application settings for a given section, or just show/display current settings.',
)
@click.pass_context
def configure(ctx, section: str, set: bool):
    """
    Define and store configuration values for a given section in the config file.
    """
    if not section.lower() in ['wifi', 'data', 'speedtest', 'all']:
        raise click.BadParameter("Invalid section '{}'".format(section))

    if set:
        save_settings(ctx.obj['globals'], section.lower())
    else:
        show_settings(ctx.obj['globals'], section.lower())


# ---------------------------------------------------------
# CMD: creds
# ---------------------------------------------------------
@main.command()
@click.option(
    '--how',
    type = click.Choice(['terminal', 'png'], case_sensitive=False),
    default = 'terminal',
    help = 'Display QR code with WiFi creds in terminal or save to file.',
)
@click.option(
    '--filename', 
    type = click.Path(),
    default = '',
    help = 'Full path to PNG file')
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
        if filename.strip() == '':
            # @todo Check if path to file exists.
            #       If not, create req'd dirs
            filename = '{}/{}-QR.png'.format(Path.home(),str(ctx.obj['settings']['wifi']['ssid']).upper().replace(' ','-'))
        
        qr.png(filename, scale=10)
        click.echo("Saved QR code to '{}'".format(filename))
    
    
# ---------------------------------------------------------
# CMD: speedtest
# ---------------------------------------------------------
@main.command()
@click.option(
    '--display',
    type = click.Choice(['stdout', 'epaper', 'none'], case_sensitive=False),
    default = 'stdout',
    help = 'Display speed test data on STDOUT or ePaper screen.',
)
@click.option(
    '--save/--no-save',
    default = True,
    help = 'Save speed test data to data storage.',
)
@click.option(
    '--count',
    type = click.IntRange(1, APP_MAX_RUNS, clamp=True),
    default = 1,
    help = 'Number (1-100) of tests to run in sequence.',
)
@click.pass_context
def speedtest(ctx, display: str, save: bool, count: int):
    """
    Get speed test data.
    """
    ctx.obj['settings'] = read_settings(ctx.obj['globals'])
    if not isvalid_settings(ctx.obj['settings']):
        raise click.ClickException("Invalid and/or incomplete config info!")
    
    data = []
    
    for i in range(0, count):
        data.append(get_speed_data(ctx.obj['settings']))

        if display.lower() == 'stdout':
            click.echo('-- Test {} of {} --'.format(str(i + 1), str(count)))
            click.echo('DATE: {} {}'.format(time.strftime('%m/%d/%y', time.localtime(data[i]['time'])), time.strftime('%H:%M', time.localtime(data[i]['time']))))
            click.echo('PING: {} ms'.format(data[i]['ping']))
            click.echo('DOWN: {} Mbit/s'.format(data[i]['download']))
            click.echo('UP:   {} Mbit/s'.format(data[i]['upload']))

        elif display.lower() == 'epaper':
            #
            #
            click.echo('-- PRINT TO EPAPER CODE HERE --')
            #
            #
    
        if (i + 1) < count:
            time.sleep(APP_SLEEP)
        
    if save:
        save_speed_data(ctx.obj['settings'], data)
         
    
# ---------------------------------------------------------
# CMD: debug
# ---------------------------------------------------------
@main.command()
@click.option(
    '--msg',
    default = 'Testing 1-2-3',
    help ='Display speed test data on STDOUT or ePaper screen.',
)
@click.pass_context
def debug(ctx, msg: str):
    """
    Show debug message.
    """
    click.echo(msg)
    click.echo("CONFIG: '{}'".format(ctx.obj['globals']['configFName']))
    
    


# =========================================================
#              A P P   S T A R T   S E C T I O N
# =========================================================
def start():
    main(obj = {})

if __name__ == '__main__':
    start()
    