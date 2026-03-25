import json
from collections import OrderedDict
from typing import Any, Dict
from urllib.parse import urlencode

from eth_account import Account
from eth_account.messages import encode_typed_data

from hummingbot.connector.exchange.aster import aster_constants as CONSTANTS
from hummingbot.connector.time_synchronizer import TimeSynchronizer
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest, WSRequest


class AsterAuth(AuthBase):
    def __init__(self, api_key: str, secret_key: str, time_provider: TimeSynchronizer, domain: str = "mainnet"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.time_provider = time_provider
        self.domain = domain
        self._chain_id = CONSTANTS.CHAIN_ID.get(self.domain, CONSTANTS.CHAIN_ID["mainnet"])
        try:
            self._account = Account.from_key(self.secret_key)
            self._signer_address = self._account.address
        except Exception:
            self._account = None
            self._signer_address = None

    async def rest_authenticate(self, request: RESTRequest) -> RESTRequest:
        """
        Adds the nonce, user, signer and the signature to the request, required for authenticated interactions.
        :param request: the request to be configured for authenticated interaction
        """
        if request.method == RESTMethod.POST:
            request.data = self.add_auth_to_params(params=json.loads(request.data or "{}"))
        else:
            request.params = self.add_auth_to_params(params=request.params)

        headers = {}
        if request.headers is not None:
            headers.update(request.headers)
        headers.update(self.header_for_authentication())
        request.headers = headers

        return request

    async def ws_authenticate(self, request: WSRequest) -> WSRequest:
        """
        This method is intended to configure a websocket request to be authenticated. Aster does not use this
        functionality
        """
        return request  # pass-through

    def add_auth_to_params(self, params: Dict[str, Any]):
        # Nonce in microseconds
        nonce = int(self.time_provider.time() * 1e6)

        request_params = OrderedDict(params or {})
        request_params["nonce"] = str(nonce)
        request_params["user"] = self.api_key
        request_params["signer"] = self._signer_address or ""

        signature = self._generate_signature(params=request_params)
        request_params["signature"] = signature

        return request_params

    def header_for_authentication(self) -> Dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key}

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        if not self.secret_key:
            return ""

        encoded_params_str = urlencode(params)

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
                "chainId": self._chain_id,
                "verifyingContract": "0x0000000000000000000000000000000000000000"
            },
            "message": {
                "msg": encoded_params_str
            }
        }

        signable_message = encode_typed_data(full_message=typed_data)
        signed_message = Account.sign_message(signable_message, private_key=self.secret_key)
        return signed_message.signature.hex()
