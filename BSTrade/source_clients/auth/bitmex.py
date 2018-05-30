import hashlib
import hmac
from urllib.parse import urlparse


api_keys = {
    'test': {
        'order': {
            'key': 'l7_plzAf_ra-FgSfSyH8qfrF',
            'secret': '4aIzQCBQHyShkqMFzuUuNVE91BBsag_V4eFFb0H1rArGswSY',
            'withdraw': False
        },
        'cancel': {
            'key': 'X1tFxx4CNvlnzPqCIvPzB-RT',
            'secret': 'YNlDtadyvBpMMc9DL_kmiQiVEVmjjEGq21C5QKlUNt7zYFbC',
            'withdraw': False
        },
    },

    'real': {
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
    }
}


# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + expires + data), hex encoded.
# Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
# and the data, if present, must be JSON without whitespace between keys.
def generate_signature(secret, verb, url, expires, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsed_url = urlparse(url)
    path = parsed_url.path
    if parsed_url.query:
        path = path + '?' + parsed_url.query

    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')

    print("Computing HMAC: %s" % verb + path + str(expires) + data)
    message = verb + path + str(expires) + data

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature

