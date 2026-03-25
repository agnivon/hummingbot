import unittest

from hummingbot.connector.exchange.aster import aster_utils as utils


class AsterUtilTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.base_asset = "COINALPHA"
        cls.quote_asset = "HBOT"
        cls.trading_pair = f"{cls.base_asset}-{cls.quote_asset}"
        cls.hb_trading_pair = f"{cls.base_asset}-{cls.quote_asset}"
        cls.ex_trading_pair = f"{cls.base_asset}{cls.quote_asset}"

    def test_is_exchange_information_valid(self):
        invalid_info_1 = {
            "status": "BREAK",
        }
        self.assertFalse(utils.is_exchange_information_valid(invalid_info_1))

        invalid_info_2 = {
            "status": "HALT",
        }
        self.assertFalse(utils.is_exchange_information_valid(invalid_info_2))

        valid_info = {
            "status": "TRADING",
        }
        self.assertTrue(utils.is_exchange_information_valid(valid_info))
