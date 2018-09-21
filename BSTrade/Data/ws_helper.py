import time

from BSTrade.Api.auth import bitmex
from BSTrade.Data.const import Exchange

config = {
    Exchange.BITMEX: {
        'api_keys': {
            'order': {
                'key': 'FET28WgQOItvUlOqfgOEBGIG',
                'secret': 'Fq7kxxLhrIWoxIyMi6sZ-GsQ7mKQlW1f98FDVIJ5BP8BqdOI',
                'withdraw': False
            },
            'cancel': {
                'key': 'NzhkOFTTVp2oTJk0oyyutwCt',
                'secret': '-1mK7vfPQCHEU_40MK4kj2arsTHoMycb_-MvrfbmDn_C29R3',
                'withdraw': False
            }
        },
        'endpoint': 'wss://www.bitmex.com/realtime',
        'open_with_auth': True
    }
}


def make_auth_header(prov):
    if prov == Exchange.BITMEX:
        method = 'GET'
        api_key = config[prov]['api_keys']['order']['key']
        api_secret = config[prov]['api_keys']['order']['secret']
        expires = int(round(time.time()) + 5)

        sign = bitmex.generate_signature(
            api_secret,
            method,
            '/realtime',
            expires,
            ''
        )

        return {
            'api-expires': str(expires),
            'api-key': api_key,
            'api-signature': sign
        }
