import requests
import os
import re
import numpy as np
import pyqrcode as pq
import click

from .utils.settings import read_settings, write_settings



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
    default='~/.wifi2.cfg',
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
    configFName = os.path.expanduser(config)
    if os.path.exists(configFName):
        ctx.obj['configFName'] = configFName
        ctx.obj['settings'] = read_settings(configFName)
        click.echo("TEST-V1: {}".format(ctx.obj['settings']['test']['v1']))
        click.echo("TEST-V2: {}".format(ctx.obj['settings']['test']['v2']))
        click.echo("TEST-V3: {}".format(ctx.obj['settings']['test']['v3']))
    #    with open(filename) as cfg:
    #        api_key = cfg.read()
    #
    else:
        raise click.ClickException("Config file '{}' does NOT exist".format(configFName))

        
        
@main.command()
@click.option(
    '--ssid',
    default='',
    help='WiFi SSID name.',
)
@click.option(
    '--security',
    type=click.Choice(['WEP', 'WPA', '']),
    default='',
    help='WiFi security protocol.',
)
@click.option(
    '--pswd', '--password',
    default='',
    help='WiFi password.',
)
@click.option(
    '--data',
    type=click.Path(),
    default='JSON:~/wifi2.json',
    help='Name of WiFi stats data file. If JSON file exists, it will be overwritten.',
)
@click.pass_context
def configure(ctx, ssid: str = '', security: str = '', pswd: str = '', data: str = ''):
    """
    Store configuration values in a file.
    """
    pass
    
    #config_file = ctx.obj['config_file']

    #api_key = click.prompt(
    #    "Please enter your API key",
    #    default=ctx.obj.get('api_key', '')
    #)

    #with open(config_file, 'w') as cfg:
    #    cfg.write(api_key)
    

    
    
@main.command()
@click.argument('show-how')
@click.pass_context
def show_qr(ctx, show_how):
    """
    Show QR code for WiFi credentials.
    """
    api_key = ctx.obj['api_key']

    weather = current_weather(location, api_key)
    print(f"The weather in {location} right now: {weather}.")
    
    
@main.command()
@click.argument('msg')
@click.pass_context
def show_msg(ctx, msg: str = 'Testing 1-2-3'):
    """
    Show message.
    """
    click.echo(msg)
    


def start():
    main(obj={})

if __name__ == '__main__':
    start()
    