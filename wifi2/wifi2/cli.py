import requests
import os
import re
import numpy as np
import pyqrcode as pq
import click

from .utils.settings import read_settings, save_settings, isvalid_settings
from .utils.qr import wifi_qr



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
@click.group()
@click.option(
    '--config',
    type=click.Path(),
    default='~/.wifi2.ini',
    help='Name of config file to use.',
)
@click.pass_context
def main(ctx, config: str = ''):
    """
    Blah blah blah blah blah blah blah blah blah blah blah blah
    blah blah blah blah blah blah blah:
    
    \b
    1. Blah blah
    2. Blah blah
    
    Blah blah blah blah blah blah blah blah blah blah blah blah
     blah blah.
    """
    
    ctx.obj['configFName'] = os.path.expanduser(config)
        
        
@main.command()
@click.option(
    '--section',
    type=click.Choice(['wifi', 'data', 'speedtest']),
    default='',
    help='Config file section name.',
)
@click.pass_context
def configure(ctx, section: str = ''):
    """
    Define and store configuration values for a given section in the config file.
    """
    if section.lower() in ['wifi', 'data', 'speedtest']:
        save_settings(ctx.obj['configFName'], section.lower())
    else:
        raise click.BadParameter("Invalid section '{}'".format(section))
    
    
@main.command()
@click.option(
    '--show-how',
    type=click.Choice(['terminal', 'png']),
    default='terminal',
    help='Display QR code in terminal or save to file.',
)
@click.option('--filename', help='full path to the png file')
@click.pass_context
def show_qr(ctx, show_how, filename=''):
    """
    Show QR code for WiFi credentials.
    """
    ctx.obj['settings'] = read_settings(ctx.obj['configFName'])
    if not isvalid_settings(ctx.obj['settings']):
        raise click.ClickException("Invalid and/or incomplete config info!")

    qr = wifi_qr(ctx.obj['settings']['wifi']['ssid'], ctx.obj['settings']['wifi']['security'], ctx.obj['settings']['wifi']['password'])
        
    if show_how.lower() == 'terminal':
        #print(qr.terminal())
        click.echo(qr.terminal())
    else:
        #scale = 10
        #qr.png(filename, scale)
        click.echo('Saving QR code to some file somewhere')
    
    
@main.command()
@click.argument('msg')
@click.pass_context
def show_msg(ctx, msg: str = 'Testing 1-2-3'):
    """
    Show message.
    """
    click.echo(msg)


# =========================================================
#              A P P   S T A R T   S E C T I O N
# =========================================================
def start():
    main(obj={})

if __name__ == '__main__':
    start()
    