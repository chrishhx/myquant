from quant.core.event import *
from quant.core.datahandler import KField
from quant.core.portfolio import Portfolio
from quant.core.riskmanager import RiskManager
from quant.data.sqlitedatahandler import SQLiteDataHandler

from typing import cast


class TurtleMgr(RiskManager):
    def __init__(self, portfolio: Portfolio):
        super(TurtleMgr, self).__init__(portfolio)
        self.data_handler: SQLiteDataHandler = cast(SQLiteDataHandler, self.data_handler)

    def on_signal(self, event: SignalEvent):
        close_event, other_event = [], []
        timestamp = event.timestamp
        total = self.portfolio.total

        for signal in event.signals:
            symbol = signal.symbol
            lot_size = self.data_handler.get_lot_size(symbol)
            close = self.data_handler.get_latest_bar_value(symbol, KField.close)

            if signal.signal_type == Signal.OpenLong or signal.signal_type == Signal.OpenShort:
                available = total * 0.01 / signal.attr['atr']
                one_hand = lot_size * close
                position = int(available / one_hand) * lot_size  # 头衬
                if position > 0 and self.portfolio.is_affordable(symbol, position):
                    # timestamp: datetime, symbol: str, order_type: str, quantity: int, direction: str, attr: dict
                    if signal.signal_type == Signal.OpenLong:
                        other_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.BUY, attr=signal.attr))
                    else:
                        other_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.SELL, attr=signal.attr))
            elif signal.signal_type == Signal.Extend:
                fill_event = self.portfolio.get_first_fill_event(symbol)
                position = abs(fill_event.quantity)
                if self.portfolio.is_affordable(symbol, position):
                    if fill_event.direction == FillEvent.BUY:
                        other_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.BUY, attr=signal.attr))
                    else:  # fill_event.direction == FillEvent.SELL
                        other_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.SELL, attr=signal.attr))
            elif signal.signal_type == Signal.Close:
                fill_event = self.portfolio.get_first_fill_event(symbol)
                position = abs(self.portfolio.get_position(symbol))
                if fill_event.direction == FillEvent.BUY:
                    close_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                  OrderEvent.SELL, attr=signal.attr))
                else:  # fill_event.direction == FillEvent.SELL
                    close_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                  OrderEvent.BUY, attr=signal.attr))
            else:
                print("lighten is not allowed, skip this event!")

        for event in close_event:
            self.events.put(event)

        for event in other_event:
            self.events.put(event)
