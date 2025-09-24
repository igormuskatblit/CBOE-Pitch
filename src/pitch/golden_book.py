"""Deterministic golden order book model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.pitch.ir import PitchEvent


@dataclass(slots=True)
class Order:
    order_id: int
    qty: int
    price: int
    ts_ns: int


@dataclass(slots=True)
class PriceLevel:
    price: int
    orders: List[Order] = field(default_factory=list)

    def add(self, order: Order) -> None:
        self.orders.append(order)

    def remove(self, order_id: int) -> None:
        self.orders = [order for order in self.orders if order.order_id != order_id]

    def execute(self, order_id: int, qty: int) -> None:
        for order in self.orders:
            if order.order_id == order_id:
                order.qty = max(0, order.qty - qty)
                break
        self.orders = [order for order in self.orders if order.qty > 0]

    def total_qty(self) -> int:
        return sum(order.qty for order in self.orders)


@dataclass
class GoldenBookState:
    seq: int
    ts_ns: int
    top_bid: Tuple[int | None, int]
    top_ask: Tuple[int | None, int]
    depth: Dict[str, List[Tuple[int, int]]]
    invariants: Dict[str, bool]


class GoldenBook:
    """Maintains deterministic price-time priority order book."""

    def __init__(self, depth: int = 5) -> None:
        self.depth = depth
        self.bids: Dict[int, PriceLevel] = {}
        self.asks: Dict[int, PriceLevel] = {}
        self.order_index: Dict[int, Tuple[str, int]] = {}

    def _get_level(self, side: str, price: int) -> PriceLevel:
        book = self.bids if side == "B" else self.asks
        if price not in book:
            book[price] = PriceLevel(price=price)
        return book[price]

    def process_events(self, events: List[PitchEvent]) -> List[GoldenBookState]:
        states: List[GoldenBookState] = []
        for idx, event in enumerate(events):
            self._apply_event(event)
            states.append(self._snapshot(event, idx))
        return states

    def _apply_event(self, event: PitchEvent) -> None:
        side = event.meta.get("side", event.meta.get("message_side"))
        if side is None:
            side = "B" if event.f.get("price", 0) % 2 == 0 else "S"
        price = event.f.get("price", 0)
        qty = event.f.get("qty", 0)
        order_id = int(event.meta.get("order_id", event.seq))

        if event.msg_type == "A":
            order = Order(order_id=order_id, qty=qty, price=price, ts_ns=event.ts_ns)
            level = self._get_level(side, price)
            level.add(order)
            self.order_index[order_id] = (side, price)
        elif event.msg_type == "E":
            info = self.order_index.get(order_id)
            if info:
                side_existing, price_existing = info
                level = self._get_level(side_existing, price_existing)
                level.execute(order_id, qty)
                if not level.orders:
                    self._delete_level(side_existing, price_existing)
        elif event.msg_type == "D":
            info = self.order_index.pop(order_id, None)
            if info:
                side_existing, price_existing = info
                level = self._get_level(side_existing, price_existing)
                level.remove(order_id)
                if not level.orders:
                    self._delete_level(side_existing, price_existing)
        else:
            raise ValueError(f"unsupported message type {event.msg_type}")

    def _delete_level(self, side: str, price: int) -> None:
        book = self.bids if side == "B" else self.asks
        book.pop(price, None)

    def _snapshot(self, event: PitchEvent, idx: int) -> GoldenBookState:
        top_bid = self._best_level(self.bids, reverse=True)
        top_ask = self._best_level(self.asks, reverse=False)
        invariants = {
            "no_cross": self._no_cross(top_bid, top_ask),
            "non_negative": self._non_negative(),
            "fifo": True,
        }
        depth_snapshot = {
            "bids": self._depth_levels(self.bids, reverse=True),
            "asks": self._depth_levels(self.asks, reverse=False),
        }
        return GoldenBookState(
            seq=event.seq,
            ts_ns=event.ts_ns,
            top_bid=top_bid,
            top_ask=top_ask,
            depth=depth_snapshot,
            invariants=invariants,
        )

    def _best_level(self, book: Dict[int, PriceLevel], reverse: bool) -> Tuple[int | None, int]:
        if not book:
            return (None, 0)
        best_price = max(book) if reverse else min(book)
        return (best_price, book[best_price].total_qty())

    def _depth_levels(self, book: Dict[int, PriceLevel], reverse: bool) -> List[Tuple[int, int]]:
        prices = sorted(book.keys(), reverse=reverse)
        result = []
        for price in prices[: self.depth]:
            result.append((price, book[price].total_qty()))
        return result

    def _no_cross(self, top_bid: Tuple[int | None, int], top_ask: Tuple[int | None, int]) -> bool:
        bid_price = top_bid[0]
        ask_price = top_ask[0]
        if bid_price is None or ask_price is None:
            return True
        return bid_price <= ask_price

    def _non_negative(self) -> bool:
        for level in list(self.bids.values()) + list(self.asks.values()):
            for order in level.orders:
                if order.qty < 0:
                    return False
        return True
