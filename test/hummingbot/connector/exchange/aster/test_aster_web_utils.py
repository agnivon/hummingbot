import unittest

import hummingbot.connector.exchange.aster.aster_constants as CONSTANTS
from hummingbot.connector.exchange.aster import aster_web_utils as web_utils


class AsterWebUtilsTestCases(unittest.TestCase):

    def test_public_rest_url_mainnet(self):
        path_url = "/TEST_PATH"
        expected_url = CONSTANTS.REST_URL["mainnet"] + CONSTANTS.PUBLIC_API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.public_rest_url(path_url))

    def test_public_rest_url_testnet(self):
        path_url = "/TEST_PATH"
        expected_url = CONSTANTS.REST_URL["testnet"] + CONSTANTS.PUBLIC_API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.public_rest_url(path_url, domain="testnet"))

    def test_private_rest_url_mainnet(self):
        path_url = "/TEST_PATH"
        expected_url = CONSTANTS.REST_URL["mainnet"] + CONSTANTS.PRIVATE_API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.private_rest_url(path_url))

    def test_private_rest_url_testnet(self):
        path_url = "/TEST_PATH"
        expected_url = CONSTANTS.REST_URL["testnet"] + CONSTANTS.PRIVATE_API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.private_rest_url(path_url, domain="testnet"))
