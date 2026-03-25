from hummingbot.core.api_throttler.data_types import LinkedLimitWeightPair, RateLimit
from hummingbot.core.data_type.in_flight_order import OrderState

# ===== Aster Spot Domain =====
DEFAULT_DOMAIN = "mainnet"

HBOT_ORDER_ID_PREFIX = "x-HBOT"
MAX_ORDER_ID_LEN = 36  # Aster allows up to 36 chars

# ===== Base URLs =====
REST_URL = {
    "mainnet": "https://sapi.asterdex.com/api/",
    "com": "https://sapi.asterdex.com/api/",
    "testnet": "https://sapi.asterdex-testnet.com/api/"
}
WSS_URL = {
    "mainnet": "wss://sstream.asterdex.com/ws",
    "com": "wss://sstream.asterdex.com/ws",
    "testnet": "wss://sstream.asterdex-testnet.com/ws"
}
USER_STREAM_WSS_URL = {
    "mainnet": "wss://sstream.asterdex.com/ws-api/v3",
    "com": "wss://sstream.asterdex.com/ws-api/v3",
    "testnet": "wss://sstream.asterdex-testnet.com/ws-api/v3"
}

CHAIN_ID = {
    "mainnet": 1666,
    "com": 1666,
    "testnet": 714
}

PUBLIC_API_VERSION = "v3"
PRIVATE_API_VERSION = "v3"

# ===== Public API Endpoints =====
PING_PATH_URL = "/ping"
SERVER_TIME_PATH_URL = "/time"
EXCHANGE_INFO_PATH_URL = "/exchangeInfo"
SNAPSHOT_PATH_URL = "/depth"
RECENT_TRADES_PATH_URL = "/trades"
AGG_TRADES_PATH_URL = "/aggTrades"
KLINES_PATH_URL = "/klines"

TICKER_PRICE_CHANGE_PATH_URL = "/ticker/24hr"
TICKER_BOOK_PATH_URL = "/ticker/bookTicker"
PRICES_PATH_URL = "/ticker/price"

# ===== Private API Endpoints =====
ACCOUNTS_PATH_URL = "/account"
MY_TRADES_PATH_URL = "/userTrades"
ORDER_PATH_URL = "/order"
OPEN_ORDERS_PATH_URL = "/openOrders"
ALL_ORDERS_PATH_URL = "/allOrders"
ASTER_USER_STREAM_PATH_URL = "/listenKey"
COMMISSION_RATE_PATH_URL = "/commissionRate"

# ===== WebSocket =====
WS_HEARTBEAT_TIME_INTERVAL = 180  # server ping every 3 minutes

# ===== Order Sides =====
SIDE_BUY = "BUY"
SIDE_SELL = "SELL"

# ===== Time in Force =====
TIME_IN_FORCE_GTC = "GTC"
TIME_IN_FORCE_IOC = "IOC"
TIME_IN_FORCE_FOK = "FOK"
TIME_IN_FORCE_GTX = "GTX"  # post-only (Aster supported)

# ===== Rate Limit Types =====
REQUEST_WEIGHT = "REQUEST_WEIGHT"
ORDERS = "ORDERS"

# ===== Time Intervals =====
ONE_MINUTE = 60
TEN_SECONDS = 10

MAX_REQUEST = 5000

# ===== Order State Mapping =====
ORDER_STATE = {
    "NEW": OrderState.OPEN,
    "PARTIALLY_FILLED": OrderState.PARTIALLY_FILLED,
    "FILLED": OrderState.FILLED,
    "CANCELED": OrderState.CANCELED,
    "REJECTED": OrderState.FAILED,
    "EXPIRED": OrderState.FAILED,
}

# ===== WebSocket Event Types =====
DIFF_EVENT_TYPE = "depthUpdate"
TRADE_EVENT_TYPE = "trade"

# ===== Rate Limits (Aster Spot) =====
RATE_LIMITS = [
    # Global pools
    RateLimit(limit_id=REQUEST_WEIGHT, limit=6000, time_interval=ONE_MINUTE),
    RateLimit(limit_id=ORDERS, limit=6000, time_interval=ONE_MINUTE),
    RateLimit(limit_id=f"{ORDERS}_10S", limit=300, time_interval=TEN_SECONDS),
    # Endpoint weights (all weight = 1 unless specified)
    RateLimit(
        limit_id=PING_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=SERVER_TIME_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=EXCHANGE_INFO_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=SNAPSHOT_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 10)],
    ),
    RateLimit(
        limit_id=TICKER_PRICE_CHANGE_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=TICKER_BOOK_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=PRICES_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, 1)],
    ),
    RateLimit(
        limit_id=ORDER_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, 1),
            LinkedLimitWeightPair(ORDERS, 1),
        ],
    ),
    RateLimit(
        limit_id=ASTER_USER_STREAM_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, 1),
        ],
    ),
    RateLimit(
        limit_id=COMMISSION_RATE_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, 20),
        ],
    ),
    RateLimit(
        limit_id=ACCOUNTS_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, 5),
        ],
    ),
    RateLimit(
        limit_id=MY_TRADES_PATH_URL,
        limit=MAX_REQUEST,
        time_interval=ONE_MINUTE,
        linked_limits=[
            LinkedLimitWeightPair(REQUEST_WEIGHT, 5),
        ],
    ),
]

# ===== Error Codes =====
ORDER_NOT_EXIST_ERROR_CODE = -2013
ORDER_NOT_EXIST_MESSAGE = "Order does not exist"

UNKNOWN_ORDER_ERROR_CODE = -2011
UNKNOWN_ORDER_MESSAGE = "Unknown order sent"
