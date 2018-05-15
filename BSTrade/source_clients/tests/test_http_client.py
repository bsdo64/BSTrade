import pytest
from ..http_client import http_client

client = http_client()


class TestHttpClient(object):
    def test_init(self):
        client.get('http://www.naver.com')

