import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or \
            not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    #r = requests.get('{}&text={}&from={}&to={}'.format(
    #                     app.config['MS_TRANSLATOR_URL'], text, source_language, dest_language),
    #                 headers=auth)
    r = requests.get('https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&text={}&from={}&to={}'.format(
                      text, source_language, dest_language),
                      headers=auth)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))

# https://api.cognitive.microsofttranslator.com
# curl -X POST "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=zh-Hans" -H "Ocp-Apim-Subscription-Key: <client-secret>" -H "Content-Type: application/json; charset=UTF-8" -d "[{'Text':'Hello, what is your name?'}]"