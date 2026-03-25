import asyncio
import json
from unittest import TestCase
from unittest.mock import MagicMock

from eth_account import Account

from hummingbot.connector.exchange.aster.aster_auth import AsterAuth
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest


class AsterAuthTests(TestCase):

    def setUp(self) -> None:
        self._api_key = "testApiKey"
        # Test private key (32 bytes hex)
        self._secret = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # noqa: mock
        self._account = Account.from_key(self._secret)

    def async_run_with_timeout(self, coroutine, timeout: float = 1):
        return asyncio.get_event_loop().run_until_complete(asyncio.wait_for(coroutine, timeout))

    def test_rest_authenticate_mainnet(self):
        now = 1234567890.123456
        mock_time_provider = MagicMock()
        mock_time_provider.time.return_value = now

        params = {"symbol": "LTCBTC"}
        auth = AsterAuth(
            api_key=self._api_key,
            secret_key=self._secret,
            time_provider=mock_time_provider,
            domain="mainnet"
        )
        request = RESTRequest(
            method=RESTMethod.GET,
            params=params,
            is_auth_required=True,
        )

        configured_request = self.async_run_with_timeout(auth.rest_authenticate(request))

        self.assertIn("nonce", configured_request.params)
        self.assertEqual(str(int(now * 1e6)), configured_request.params["nonce"])
        self.assertEqual(self._api_key, configured_request.headers["X-MBX-APIKEY"])
        self.assertIn("signature", configured_request.params)

        signature = configured_request.params["signature"]
        self.assertFalse(signature.startswith("0x"))
        self.assertEqual(130, len(signature))

    def test_rest_authenticate_testnet(self):
        now = 1234567890.123456
        mock_time_provider = MagicMock()
        mock_time_provider.time.return_value = now

        params = {"symbol": "LTCBTC"}
        auth = AsterAuth(
            api_key=self._api_key,
            secret_key=self._secret,
            time_provider=mock_time_provider,
            domain="testnet"
        )
        request = RESTRequest(
            method=RESTMethod.GET,
            params=params,
            is_auth_required=True,
        )

        configured_request = self.async_run_with_timeout(auth.rest_authenticate(request))
        self.assertEqual(714, auth._chain_id)
        self.assertIn("signature", configured_request.params)

    def test_post_authenticate(self):
        now = 1234567890.123456
        mock_time_provider = MagicMock()
        mock_time_provider.time.return_value = now

        data = {"symbol": "LTCBTC", "quantity": 1}
        auth = AsterAuth(
            api_key=self._api_key,
            secret_key=self._secret,
            time_provider=mock_time_provider,
        )
        request = RESTRequest(
            method=RESTMethod.POST,
            data=json.dumps(data),
            is_auth_required=True,
        )

        configured_request = self.async_run_with_timeout(auth.rest_authenticate(request))

        self.assertIn("nonce", configured_request.data)
        self.assertEqual(str(int(now * 1e6)), configured_request.data["nonce"])
        self.assertIn("signature", configured_request.data)
