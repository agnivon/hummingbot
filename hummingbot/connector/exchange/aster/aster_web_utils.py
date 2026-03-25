from typing import Callable, Optional

import hummingbot.connector.exchange.aster.aster_constants as CONSTANTS
from hummingbot.connector.time_synchronizer import TimeSynchronizer
from hummingbot.connector.utils import TimeSynchronizerRESTPreProcessor
from hummingbot.core.api_throttler.async_throttler import AsyncThrottler
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest
from hummingbot.core.web_assistant.rest_pre_processors import RESTPreProcessorBase
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory


class AsterRESTPreProcessor(RESTPreProcessorBase):
    async def pre_process(self, request: RESTRequest) -> RESTRequest:
        if request.headers is None:
            request.headers = {}

        # Aster APIs use form encoding, never JSON
        if request.method in {RESTMethod.POST, RESTMethod.PUT, RESTMethod.DELETE}:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            request.headers["Content-Type"] = ""

        return request


def public_rest_url(path_url: str, domain="mainnet") -> str:
    """
    Creates a full URL for provided public REST endpoint (Aster Spot)
    """
    return f"{CONSTANTS.REST_URL[domain]}{CONSTANTS.PUBLIC_API_VERSION}{path_url}"


def private_rest_url(path_url: str, domain="mainnet") -> str:
    """
    Creates a full URL for provided private REST endpoint (Aster Spot)
    """
    return f"{CONSTANTS.REST_URL[domain]}{CONSTANTS.PRIVATE_API_VERSION}{path_url}"


def build_api_factory(
    throttler: Optional[AsyncThrottler] = None,
    time_synchronizer: Optional[TimeSynchronizer] = None,
    time_provider: Optional[Callable] = None,
    auth: Optional[AuthBase] = None,
    domain: str = "mainnet",
) -> WebAssistantsFactory:
    throttler = throttler or create_throttler()
    time_synchronizer = time_synchronizer or TimeSynchronizer()

    time_provider = time_provider or (lambda: get_current_server_time(throttler=throttler, domain=domain))

    return WebAssistantsFactory(
        throttler=throttler,
        auth=auth,
        rest_pre_processors=[
            TimeSynchronizerRESTPreProcessor(
                synchronizer=time_synchronizer,
                time_provider=time_provider,
            ),
            AsterRESTPreProcessor(),
        ],
    )


def build_api_factory_without_time_synchronizer_pre_processor(
    throttler: AsyncThrottler,
) -> WebAssistantsFactory:
    return WebAssistantsFactory(
        throttler=throttler,
        rest_pre_processors=[
            AsterRESTPreProcessor(),
        ],
    )


def create_throttler() -> AsyncThrottler:
    return AsyncThrottler(CONSTANTS.RATE_LIMITS)


async def get_current_server_time(throttler: Optional[AsyncThrottler] = None, domain: str = "") -> float:
    throttler = throttler or create_throttler()

    api_factory = build_api_factory_without_time_synchronizer_pre_processor(throttler=throttler)
    rest_assistant = await api_factory.get_rest_assistant()

    response = await rest_assistant.execute_request(
        url=public_rest_url(CONSTANTS.SERVER_TIME_PATH_URL, domain=domain),
        method=RESTMethod.GET,
        throttler_limit_id=CONSTANTS.SERVER_TIME_PATH_URL,
    )

    return response["serverTime"]
