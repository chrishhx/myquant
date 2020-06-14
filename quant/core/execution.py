#!/usr/bin/python
# -*- coding: utf-8 -*-
import queue
from abc import ABCMeta, abstractmethod
from typing import List

from quant.core.datahandler import DataHandler
from quant.core.event import OrderEvent
from quant.core.portfolio import Portfolio


class ExecutionHandler(object, metaclass=ABCMeta):
    """
    The ExecutionHandler abstract class handles the interaction
    between a set of order objects generated by a Portfolio and
    the ultimate set of Fill objects that actually occur in the
    market. 

    The handlers can be used to subclass simulated brokerages
    or live brokerages, with identical interfaces. This allows
    strategies to be backtested in a very similar manner to the
    live trading engine.
    """

    def __init__(self, portfolio: Portfolio):
        self.portfolio: Portfolio = portfolio
        self.events: queue.Queue = portfolio.events
        self.symbol_list: List[str] = portfolio.symbol_list
        self.data_handler: DataHandler = portfolio.data_handler

    @abstractmethod
    def on_order(self, event: OrderEvent):
        """
        Takes an Order event and executes it, producing
        a Fill event that gets placed onto the Events queue.

        Parameters:
        event - Contains an Event object with order information.
        """
        raise NotImplementedError("Should implement exec_order()")
