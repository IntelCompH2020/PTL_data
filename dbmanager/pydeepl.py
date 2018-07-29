"""
Class adapted from github project
https://github.com/EmilioK97/pydeepl

This project provided a wrapper for DeepL, when it was a free translation
service. Now, the original project code would not work, and thus it needs
to be upadated
"""

import requests
import ipdb

BASE_URL = 'https://api.deepl.com/v1/translate'
Key = 'af57cd8e-0dcb-832a-2f22-55f3134043c1'

LANGUAGES = {
    'auto': 'Auto',
    'DE': 'German',
    'EN': 'English',
    'FR': 'French',
    'ES': 'Spanish',
    'IT': 'Italian',
    'NL': 'Dutch',
    'PL': 'Polish'
}

class TranslationError(Exception):
    def __init__(self, message):
        super(TranslationError, self).__init__(message)

def deepL_translate(text):
    if text is None:
        raise TranslationError('Text can\'t be None.')
    if len(text) > 5000:
        raise TranslationError('Text too long (limited to 5000 characters).')
    # if to_lang not in LANGUAGES.keys():
    #     raise TranslationError('Language {} not available.'.format(to_lang))
    # if from_lang is not None and from_lang not in LANGUAGES.keys():
    #     raise TranslationError('Language {} not available.'.format(from_lang))

    text = text.replace(' ', '%20')
    data = 'auth_key='+Key+'&text='+text+'&target_lang=EN&source_lang=ES'
    headers = {  'Content-Type':'application/x-www-form-urlencoded',
                 'Content-Length':str(len(text))
                }
    

    response = requests.post(BASE_URL, headers=headers, data=data).json()
    print(response)
    translations = response['translations'][0]['text']

    if len(translations) == 0:
        print(response)
        raise TranslationError('No translations found.')
    else:
        return translations
