from decimal import Decimal

from pydantic import ConfigDict, Field, SecretStr

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0.0002"),  # 0.02%
    taker_percent_fee_decimal=Decimal("0.0004"),  # 0.04%
    buy_percent_fee_deducted_from_returns=True,
)

CENTRALIZED = True

EXAMPLE_PAIR = "BTC-USDT"

BROKER_ID = "x-hummingbot"


class AsterPerpetualConfigMap(BaseConnectorConfigMap):
    connector: str = "aster_perpetual"

    aster_perpetual_api_key: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": "Enter your Aster Perpetual API key (for V3 use 'user:signer' format)",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )

    aster_perpetual_api_secret: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": "Enter your Aster Perpetual API secret (for V3 enter your private key)",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )

    model_config = ConfigDict(title="aster_perpetual")


KEYS = AsterPerpetualConfigMap.model_construct()

OTHER_DOMAINS = ["aster_perpetual_testnet"]
OTHER_DOMAINS_PARAMETER = {"aster_perpetual_testnet": "aster_perpetual_testnet"}
OTHER_DOMAINS_EXAMPLE_PAIR = {"aster_perpetual_testnet": "BTC-USDT"}
OTHER_DOMAINS_DEFAULT_FEES = {"aster_perpetual_testnet": [0.02, 0.04]}


class AsterPerpetualTestnetConfigMap(BaseConnectorConfigMap):
    connector: str = "aster_perpetual_testnet"

    aster_perpetual_testnet_api_key: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": "Enter your Aster Perpetual testnet API key (for V3 use 'user:signer' format)",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )

    aster_perpetual_testnet_api_secret: SecretStr = Field(
        default=...,
        json_schema_extra={
            "prompt": "Enter your Aster Perpetual testnet API secret (for V3 enter your private key)",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        },
    )

    model_config = ConfigDict(title="aster_perpetual_testnet")


OTHER_DOMAINS_KEYS = {"aster_perpetual_testnet": AsterPerpetualTestnetConfigMap.model_construct()}
