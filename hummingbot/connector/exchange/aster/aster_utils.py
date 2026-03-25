from decimal import Decimal
from typing import Any, Dict

from pydantic import ConfigDict, Field, SecretStr

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

CENTRALIZED = False
EXAMPLE_PAIR = "BNBUSDT"

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0.0002"),
    taker_percent_fee_decimal=Decimal("0.0004"),
    buy_percent_fee_deducted_from_returns=True,
)


def is_exchange_information_valid(exchange_info: Dict[str, Any]) -> bool:
    """
    Verifies if a trading pair is enabled to operate based on Aster exchange information
    :param exchange_info: the exchange information for a trading pair
    :return: True if the trading pair is enabled, False otherwise
    """
    # Aster Spot only exposes `status`
    return exchange_info.get("status") == "TRADING"


class AsterConfigMap(BaseConnectorConfigMap):
    connector: str = "aster"

    aster_api_key: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": lambda cm: "Enter your Aster API key",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )

    aster_api_secret: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": lambda cm: "Enter your Aster API secret",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )
    domain: str = Field(
        default="mainnet",
        json_schema_extra={
            "prompt": lambda cm: "Enter your Aster domain (mainnet/testnet)",
            "prompt_on_new": True,
        },
    )

    model_config = ConfigDict(title="aster")


KEYS = AsterConfigMap.model_construct()
