import asyncio
import copy
import hashlib
import hmac
import json
import unittest
from typing import Awaitable
from urllib.parse import urlencode

import hummingbot.connector.derivative.aster_perpetual.aster_perpetual_constants as CONSTANTS
from hummingbot.connector.derivative.aster_perpetual.aster_perpetual_auth import AsterPerpetualAuth
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest, WSJSONRequest


class AsterPerpetualAuthUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ev_loop = asyncio.get_event_loop()
        cls.api_key = "TEST_API_KEY"
        cls.secret_key = "TEST_SECRET_KEY"

    def setUp(self) -> None:
        super().setUp()
        self.emulated_time = 1640001112.223
        self.test_params = {
            "test_param": "test_input",
            "timestamp": int(self.emulated_time * 1e3),
        }
        self.auth = AsterPerpetualAuth(api_key=self.api_key, api_secret=self.secret_key, time_provider=self)

    def _get_test_payload(self):
        return urlencode(dict(copy.deepcopy(self.test_params)))

    def _get_signature_from_test_payload(self):
        return hmac.new(self.auth._api_secret, self._get_test_payload().encode("utf-8"), hashlib.sha256).hexdigest()

    def async_run_with_timeout(self, coroutine: Awaitable, timeout: float = 1):
        ret = self.ev_loop.run_until_complete(asyncio.wait_for(coroutine, timeout))
        return ret

    def time(self):
        # Implemented to emulate a TimeSynchronizer
        return self.emulated_time

    def test_generate_signature_from_payload(self):
        payload = self._get_test_payload()
        signature = self.auth._generate_signature(payload)

        self.assertEqual(signature, self._get_signature_from_test_payload())

    def test_rest_authenticate_parameters_provided(self):
        request: RESTRequest = RESTRequest(
            method=RESTMethod.GET, url="/TEST_PATH_URL", params=copy.deepcopy(self.test_params), is_auth_required=True
        )

        signed_request: RESTRequest = self.async_run_with_timeout(self.auth.rest_authenticate(request))

        self.assertIn("X-MBX-APIKEY", signed_request.headers)
        self.assertEqual(signed_request.headers["X-MBX-APIKEY"], self.api_key)
        self.assertIn("signature", signed_request.params)
        self.assertEqual(signed_request.params["signature"], self._get_signature_from_test_payload())

    def test_rest_authenticate_data_provided(self):
        request: RESTRequest = RESTRequest(
            method=RESTMethod.POST, url="/TEST_PATH_URL", data=json.dumps(self.test_params), is_auth_required=True
        )

        signed_request: RESTRequest = self.async_run_with_timeout(self.auth.rest_authenticate(request))

        self.assertIn("X-MBX-APIKEY", signed_request.headers)
        self.assertEqual(signed_request.headers["X-MBX-APIKEY"], self.api_key)
        self.assertIn("signature", signed_request.data)
        self.assertEqual(signed_request.data["signature"], self._get_signature_from_test_payload())

    def test_ws_authenticate(self):
        request: WSJSONRequest = WSJSONRequest(
            payload={"TEST": "SOME_TEST_PAYLOAD"}, throttler_limit_id="TEST_LIMIT_ID", is_auth_required=True
        )

        signed_request: WSJSONRequest = self.async_run_with_timeout(self.auth.ws_authenticate(request))

        self.assertEqual(request, signed_request)

    def test_is_v3_detection(self):
        # HMAC-SHA256 style
        auth_v1 = AsterPerpetualAuth("key", "secret", self)
        self.assertFalse(auth_v1._is_v3)

        # Pro API-KEY style (user:signer)
        auth_v3_1 = AsterPerpetualAuth("user:signer", "secret", self)
        self.assertTrue(auth_v3_1._is_v3)

        # Private key style (64 or 66 chars)
        auth_v3_2 = AsterPerpetualAuth("key", "a" * 64, self)
        self.assertTrue(auth_v3_2._is_v3)

    def test_v3_signature_generation_mainnet(self):
        # Domain 1666 for mainnet
        api_key = "user:signer"
        api_secret = "0x" + "a" * 64
        auth = AsterPerpetualAuth(api_key, api_secret, self, domain=CONSTANTS.DOMAIN)

        request = RESTRequest(
            method=RESTMethod.POST,
            url="/TEST_PATH",
            params={"symbol": "BTC-USDT", "side": "BUY"},
            is_auth_required=True,
        )

        signed_request = self.async_run_with_timeout(auth.rest_authenticate(request))
        self.assertIn("signature", signed_request.data)
        self.assertEqual(signed_request.data["user"], "user")
        self.assertEqual(signed_request.data["signer"], "signer")

    def test_v3_signature_generation_testnet(self):
        # Domain 714 for testnet
        api_key = "user:signer"
        api_secret = "0x" + "a" * 64
        auth = AsterPerpetualAuth(api_key, api_secret, self, domain=CONSTANTS.TESTNET_DOMAIN)

        request = RESTRequest(
            method=RESTMethod.POST,
            url="/TEST_PATH",
            params={"symbol": "BTC-USDT", "side": "BUY"},
            is_auth_required=True,
        )

        signed_request = self.async_run_with_timeout(auth.rest_authenticate(request))
        self.assertIn("signature", signed_request.data)
        # The signature itself will be different because chainId changed to 714
        self.assertGreater(len(signed_request.data["signature"]), 100)
