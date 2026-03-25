import asyncio
import time
from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional

import hummingbot.connector.derivative.aster_perpetual.aster_perpetual_constants as CONSTANTS
import hummingbot.connector.derivative.aster_perpetual.aster_perpetual_web_utils as web_utils
from hummingbot.core.data_type.common import TradeType
from hummingbot.core.data_type.funding_info import FundingInfo, FundingInfoUpdate
from hummingbot.core.data_type.order_book_message import OrderBookMessage, OrderBookMessageType
from hummingbot.core.data_type.perpetual_api_order_book_data_source import PerpetualAPIOrderBookDataSource
from hummingbot.core.web_assistant.connections.data_types import WSJSONRequest
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory
from hummingbot.core.web_assistant.ws_assistant import WSAssistant
from hummingbot.logger import HummingbotLogger

if TYPE_CHECKING:
    from hummingbot.connector.derivative.aster_perpetual.aster_perpetual_derivative import AsterPerpetualDerivative


class AsterPerpetualAPIOrderBookDataSource(PerpetualAPIOrderBookDataSource):
    _bpobds_logger: Optional[HummingbotLogger] = None
    _trading_pair_symbol_map: Dict[str, Mapping[str, str]] = {}
    _mapping_initialization_lock = asyncio.Lock()

    def __init__(
        self,
        trading_pairs: List[str],
        connector: "AsterPerpetualDerivative",
        api_factory: WebAssistantsFactory,
        domain: str = CONSTANTS.DOMAIN,
    ):
        super().__init__(trading_pairs)
        self._connector = connector
        self._api_factory = api_factory
        self._domain = domain
        self._trading_pairs = trading_pairs
        self._message_queue: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

        self._trade_messages_queue_key = CONSTANTS.TRADE_STREAM_ID
        self._diff_messages_queue_key = CONSTANTS.DIFF_STREAM_ID
        self._funding_info_messages_queue_key = CONSTANTS.FUNDING_INFO_STREAM_ID

    async def get_last_traded_prices(self, trading_pairs: List[str], domain: Optional[str] = None) -> Dict[str, float]:
        return await self._connector.get_last_traded_prices(trading_pairs=trading_pairs)

    async def get_funding_info(self, trading_pair: str) -> FundingInfo:
        info = await self._request_complete_funding_info(trading_pair)
        return FundingInfo(
            trading_pair=trading_pair,
            index_price=Decimal(info["indexPrice"]),
            mark_price=Decimal(info["markPrice"]),
            next_funding_utc_timestamp=int(info["nextFundingTime"] * 1e-3),
            rate=Decimal(info["lastFundingRate"]),
        )

    async def _request_order_book_snapshot(self, trading_pair: str) -> Dict[str, Any]:
        symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
        return await self._connector._api_get(
            path_url=CONSTANTS.SNAPSHOT_REST_URL,
            params={"symbol": symbol, "limit": 1000},
        )

    async def _order_book_snapshot(self, trading_pair: str) -> OrderBookMessage:
        snapshot = await self._request_order_book_snapshot(trading_pair)
        return OrderBookMessage(
            OrderBookMessageType.SNAPSHOT,
            {
                "trading_pair": trading_pair,
                "update_id": snapshot["lastUpdateId"],
                "bids": snapshot["bids"],
                "asks": snapshot["asks"],
            },
            timestamp=time.time(),
        )

    async def _connected_websocket_assistant(self) -> WSAssistant:
        ws = await self._api_factory.get_ws_assistant()
        await ws.connect(
            ws_url=web_utils.wss_url(CONSTANTS.PUBLIC_WS_ENDPOINT, domain=self._domain),
            ping_timeout=CONSTANTS.HEARTBEAT_TIME_INTERVAL,
        )
        return ws

    async def _subscribe_channels(self, ws: WSAssistant):
        try:
            subscriptions = [
                (self._diff_messages_queue_key, "@depth@100ms"),
                (self._trade_messages_queue_key, "@aggTrade"),
                (self._funding_info_messages_queue_key, "@markPrice"),
            ]

            for stream_id, suffix in subscriptions:
                params = []
                for pair in self._trading_pairs:
                    symbol = await self._connector.exchange_symbol_associated_to_pair(pair)
                    params.append(f"{symbol.lower()}{suffix}")

                await ws.send(
                    WSJSONRequest(
                        {
                            "method": "SUBSCRIBE",
                            "params": params,
                            "id": stream_id,
                        }
                    )
                )

            self.logger().info("Subscribed to public order book, trade and funding info channels...")

        except Exception:
            self.logger().exception("Unexpected error occurred subscribing to order book trading and delta streams...")
            raise

    async def subscribe_to_trading_pair(self, trading_pair: str):
        """
        Subscribes to the order book and trade streams for a given trading pair.
        """
        if self._connector.is_public_ws_connected():
            ws = self._connector.public_ws
            symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
            params = [
                f"{symbol.lower()}@depth@100ms",
                f"{symbol.lower()}@aggTrade",
                f"{symbol.lower()}@markPrice",
            ]
            await ws.send(
                WSJSONRequest(
                    {
                        "method": "SUBSCRIBE",
                        "params": params,
                        "id": 1,
                    }
                )
            )

    async def unsubscribe_from_trading_pair(self, trading_pair: str):
        """
        Unsubscribes from the order book and trade streams for a given trading pair.
        """
        if self._connector.is_public_ws_connected():
            ws = self._connector.public_ws
            symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
            params = [
                f"{symbol.lower()}@depth@100ms",
                f"{symbol.lower()}@aggTrade",
                f"{symbol.lower()}@markPrice",
            ]
            await ws.send(
                WSJSONRequest(
                    {
                        "method": "UNSUBSCRIBE",
                        "params": params,
                        "id": 1,
                    }
                )
            )

    def _channel_originating_message(self, event_message: Dict[str, Any]) -> str:
        stream = event_message.get("stream")
        if not stream:
            return ""

        if "@depth" in stream:
            return self._diff_messages_queue_key
        if "@aggTrade" in stream:
            return self._trade_messages_queue_key
        if "@markPrice" in stream:
            return self._funding_info_messages_queue_key
        return ""

    async def _parse_order_book_diff_message(self, raw_message: Dict[str, Any], message_queue: asyncio.Queue):
        data = raw_message["data"]
        trading_pair = await self._connector.trading_pair_associated_to_exchange_symbol(data["s"])

        message_queue.put_nowait(
            OrderBookMessage(
                OrderBookMessageType.DIFF,
                {
                    "trading_pair": trading_pair,
                    "first_update_id": data["U"],
                    "update_id": data["u"],
                    "bids": data["b"],
                    "asks": data["a"],
                },
                timestamp=data["E"] * 1e-3,
            )
        )

    async def _parse_trade_message(self, raw_message: Dict[str, Any], message_queue: asyncio.Queue):
        data = raw_message["data"]
        trading_pair = await self._connector.trading_pair_associated_to_exchange_symbol(data["s"])

        message_queue.put_nowait(
            OrderBookMessage(
                OrderBookMessageType.TRADE,
                {
                    "trading_pair": trading_pair,
                    "trade_type": float(TradeType.SELL.value) if data["m"] else float(TradeType.BUY.value),
                    "trade_id": data["a"],
                    "price": data["p"],
                    "amount": data["q"],
                },
                timestamp=data["T"] * 1e-3,
            )
        )

    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                for trading_pair in self._trading_pairs:
                    snapshot_msg: OrderBookMessage = await self._order_book_snapshot(trading_pair)
                    output.put_nowait(snapshot_msg)
                    self.logger().debug(f"Saved order book snapshot for {trading_pair}")
                delta = CONSTANTS.ONE_HOUR - time.time() % CONSTANTS.ONE_HOUR
                await self._sleep(delta)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error(
                    "Unexpected error occurred fetching orderbook snapshots. Retrying in 5 seconds...", exc_info=True
                )
                await self._sleep(5.0)

    async def _parse_funding_info_message(self, raw_message: Dict[str, Any], message_queue: asyncio.Queue):
        data = raw_message["data"]
        trading_pair = await self._connector.trading_pair_associated_to_exchange_symbol(data["s"])

        if trading_pair not in self._trading_pairs:
            return

        message_queue.put_nowait(
            FundingInfoUpdate(
                trading_pair=trading_pair,
                index_price=Decimal(data["i"]),
                mark_price=Decimal(data["p"]),
                next_funding_utc_timestamp=int(data["T"] * 1e-3),
                rate=Decimal(data["r"]),
            )
        )

    async def _request_complete_funding_info(self, trading_pair: str):
        symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
        return await self._connector._api_get(
            path_url=CONSTANTS.MARK_PRICE_URL,
            params={"symbol": symbol},
            is_auth_required=False,
        )
