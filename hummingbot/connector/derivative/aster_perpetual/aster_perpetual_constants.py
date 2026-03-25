from hummingbot.core.api_throttler.data_types import LinkedLimitWeightPair, RateLimit
from hummingbot.core.data_type.in_flight_order import OrderState

EXCHANGE_NAME = "aster_perpetual"
BROKER_ID = "x-nbQe1H39"
MAX_ORDER_ID_LEN = 36

DOMAIN = EXCHANGE_NAME
TESTNET_DOMAIN = "aster_perpetual_testnet"

PERPETUAL_BASE_URL = "https://fapi.asterdex.com/fapi/"
TESTNET_BASE_URL = "https://fapi.asterdex-testnet.com/fapi/"

PERPETUAL_WS_URL = "wss://fstream.asterdex.com/"
TESTNET_WS_URL = "wss://fstream5.asterdex-testnet.com/"
# TESTNET_WS_URL = "wss://stream.asterdex.com/"

PUBLIC_WS_ENDPOINT = "stream"
PRIVATE_WS_ENDPOINT = "ws"

TIME_IN_FORCE_GTC = "GTC"  # Good till cancelled
TIME_IN_FORCE_GTX = "GTX"  # Good Till Crossing
TIME_IN_FORCE_IOC = "IOC"  # Immediate or cancel
TIME_IN_FORCE_FOK = "FOK"  # Fill or kill

# Public API v3 Endpoints
SNAPSHOT_REST_URL = "v3/depth"
TICKER_PRICE_URL = "v3/ticker/bookTicker"
TICKER_PRICE_CHANGE_URL = "v3/ticker/24hr"
EXCHANGE_INFO_URL = "v3/exchangeInfo"
RECENT_TRADES_URL = "v3/trades"
PING_URL = "v3/ping"
MARK_PRICE_URL = "v3/premiumIndex"
SERVER_TIME_PATH_URL = "v3/time"

# Private API v3 Endpoints
ORDER_URL = "v3/order"
CANCEL_ALL_OPEN_ORDERS_URL = "v3/allOpenOrders"
ACCOUNT_TRADE_LIST_URL = "v3/userTrades"
SET_LEVERAGE_URL = "v3/leverage"
GET_INCOME_HISTORY_URL = "v3/income"
CHANGE_POSITION_MODE_URL = "v3/positionSide/dual"

POST_POSITION_MODE_LIMIT_ID = f"POST{CHANGE_POSITION_MODE_URL}"
GET_POSITION_MODE_LIMIT_ID = f"GET{CHANGE_POSITION_MODE_URL}"

# Private API v3 Endpoints
ACCOUNT_INFO_URL = "v3/account"
POSITION_INFORMATION_URL = "v3/positionRisk"

# Private API Endpoints
ASTER_USER_STREAM_ENDPOINT = "v1/listenKey"

# Funding Settlement Time Span
FUNDING_SETTLEMENT_DURATION = (0, 30)  # seconds before snapshot, seconds after snapshot

# Order Statuses
ORDER_STATE = {
    "NEW": OrderState.OPEN,
    "FILLED": OrderState.FILLED,
    "PARTIALLY_FILLED": OrderState.PARTIALLY_FILLED,
    "CANCELED": OrderState.CANCELED,
    "EXPIRED": OrderState.CANCELED,
    "REJECTED": OrderState.FAILED,
    "EXPIRED_IN_MATCH": OrderState.FAILED,
}

# Rate Limit Type
REQUEST_WEIGHT = "REQUEST_WEIGHT"
ORDERS = "ORDERS"

DIFF_STREAM_ID = 1
TRADE_STREAM_ID = 2
FUNDING_INFO_STREAM_ID = 3
HEARTBEAT_TIME_INTERVAL = 30.0

# Rate Limit time intervals
ONE_HOUR = 3600
ONE_MINUTE = 60
ONE_SECOND = 1
ONE_DAY = 86400

MAX_REQUEST = 2400

RATE_LIMITS = [
    # Pool Limits
    RateLimit(limit_id=REQUEST_WEIGHT, limit=2400, time_interval=ONE_MINUTE),
    RateLimit(limit_id=ORDERS, limit=1200, time_interval=ONE_MINUTE),
    RateLimit(limit_id=SNAPSHOT_REST_URL, limit=MAX_REQUEST, time_interval=10),
    # Public endpoints
    RateLimit(
        limit_id=SNAPSHOT_REST_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=20)],
    ),
    RateLimit(
        limit_id=TICKER_PRICE_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
    RateLimit(
        limit_id=TICKER_PRICE_CHANGE_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
    RateLimit(
        limit_id=EXCHANGE_INFO_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
    RateLimit(
        limit_id=RECENT_TRADES_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
    RateLimit(
        limit_id=MARK_PRICE_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
    # Order endpoints
    RateLimit(
        limit_id=ORDER_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
            LinkedLimitWeightPair(ORDERS, weight=1),
        ],
    ),
    RateLimit(
        limit_id=CANCEL_ALL_OPEN_ORDERS_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
            LinkedLimitWeightPair(ORDERS, weight=1),
        ],
    ),
    RateLimit(
        limit_id=SET_LEVERAGE_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
        ],
    ),
    RateLimit(
        limit_id=CHANGE_POSITION_MODE_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
        ],
    ),
    RateLimit(
        limit_id=GET_POSITION_MODE_LIMIT_ID,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
        ],
    ),
    RateLimit(
        limit_id=POST_POSITION_MODE_LIMIT_ID,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1),
        ],
    ),
    # Account / user data
    RateLimit(
        limit_id=ACCOUNT_INFO_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=5)],
    ),
    RateLimit(
        limit_id=POSITION_INFORMATION_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=5)],
    ),
    RateLimit(
        limit_id=ACCOUNT_TRADE_LIST_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=5)],
    ),
    RateLimit(
        limit_id=GET_INCOME_HISTORY_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=30)],
    ),
    # User stream
    RateLimit(
        limit_id=ASTER_USER_STREAM_ENDPOINT,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=1)],
    ),
]

ORDER_NOT_EXIST_ERROR_CODE = -2013
ORDER_NOT_EXIST_MESSAGE = "Order does not exist"
UNKNOWN_ORDER_ERROR_CODE = -2011
UNKNOWN_ORDER_MESSAGE = "Unknown order sent"
