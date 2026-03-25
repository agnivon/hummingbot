import hashlib
import hmac
import json
from collections import OrderedDict
from typing import Any, Dict
from urllib.parse import urlencode

from eth_account import Account

import hummingbot.connector.derivative.aster_perpetual.aster_perpetual_constants as CONSTANTS
from hummingbot.connector.time_synchronizer import TimeSynchronizer
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest, WSRequest


class AsterPerpetualAuth(AuthBase):
    """
    Auth class for Aster Perpetual API supporting both V1 (Binance-style) and V3 (Web3 EIP-712).
    """

    def __init__(self, api_key: str, api_secret: str, time_provider: TimeSynchronizer, domain: str = CONSTANTS.DOMAIN):
        self._api_key = api_key
        # For V3, the secret is a hex private key. We keep it as string for Account.from_key.
        # For V1, it will be used as bytes for HMAC.
        self._api_secret_str = api_secret
        self._api_secret = api_secret.encode("utf-8")
        self._time_provider = time_provider
        self._domain = domain
        self._last_nonce_ms = 0
        self._nonce_increment = 0

        # Determine if V3 based on api_key format (expecting "user:signer" for V3)
        self._is_v3 = ":" in self._api_key or len(api_secret) in {64, 66}

    @property
    def is_v3(self) -> bool:
        return self._is_v3

    def _get_nonce(self) -> int:
        now_ms = int(self._time_provider.time())
        if now_ms == self._last_nonce_ms:
            self._nonce_increment += 1
        else:
            self._last_nonce_ms = now_ms
            self._nonce_increment = 0
        return now_ms * 1_000_000 + self._nonce_increment

    def _generate_v1_signature(self, payload: str) -> str:
        return hmac.new(self._api_secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def _generate_signature(self, payload: str) -> str:
        # Legacy alias for tests
        return self._generate_v1_signature(payload)

    def _generate_v3_signature(self, payload: str) -> str:
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "Message": [
                    {"name": "msg", "type": "string"}
                ]
            },
            "primaryType": "Message",
            "domain": {
                "name": "AsterSignTransaction",
                "version": "1",
                "chainId": 714 if self._domain == CONSTANTS.TESTNET_DOMAIN else 1666,
                "verifyingContract": "0x0000000000000000000000000000000000000000"
            },
            "message": {
                "msg": payload
            }
        }
        account = Account.from_key(self._api_secret_str)
        signed_message = account.sign_typed_data(full_message=typed_data)
        return signed_message.signature.hex()

    async def rest_authenticate(self, request: RESTRequest) -> RESTRequest:
        if request.headers is None:
            request.headers = {}

        params = {}
        if request.params:
            params.update(request.params)

        if request.data:
            if isinstance(request.data, dict):
                params.update(request.data)
            elif isinstance(request.data, str):
                try:
                    params.update(json.loads(request.data))
                except Exception:
                    # Not JSON, maybe form encoded string? (Aster pre-processor converts dict to form string later)
                    pass

        if self._is_v3:
            # V3 Auth: uses 'user', 'signer', 'nonce', and 'signature'
            parts = self._api_key.split(":")
            user = parts[0]
            signer = parts[1] if len(parts) > 1 else ""  # Fallback

            params["user"] = user
            params["signer"] = signer
            params["nonce"] = self._get_nonce()

            payload = urlencode(OrderedDict(params))
            params["signature"] = self._generate_v3_signature(payload)
        else:
            # V1 Auth (Binance-style)
            params["timestamp"] = int(self._time_provider.time() * 1e3)
            payload = urlencode(OrderedDict(params))
            params["signature"] = self._generate_v1_signature(payload)
            request.headers["X-MBX-APIKEY"] = self._api_key

        if request.method == RESTMethod.POST:
            request.data = params
        else:
            request.params = params

        return request

    def header_for_authentication(self) -> Dict[str, str]:
        if self._is_v3:
            return {}
        return {"X-MBX-APIKEY": self._api_key}

    def add_auth_to_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method used by some parts of the connector.
        """
        if self._is_v3:
            parts = self._api_key.split(":")
            user = parts[0]
            signer = parts[1] if len(parts) > 1 else ""

            request_params = OrderedDict(params or {})
            request_params["user"] = user
            request_params["signer"] = signer
            request_params["nonce"] = self._get_nonce()

            payload = urlencode(request_params)
            request_params["signature"] = self._generate_v3_signature(payload)
            return dict(request_params)
        else:
            timestamp = int(self._time_provider.time() * 1e3)
            request_params = OrderedDict(params or {})
            request_params["timestamp"] = timestamp
            payload = urlencode(request_params)
            request_params["signature"] = self._generate_v1_signature(payload)
            return dict(request_params)

    async def ws_authenticate(self, request: WSRequest) -> WSRequest:
        return request  # User streams typically authenticated via listenKey
