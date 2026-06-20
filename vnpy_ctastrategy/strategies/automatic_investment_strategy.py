#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time: 2025/05/07 21:10
# @Author: yuan.xin
# @FileName: automatic_investment_strategy.py
# @Description:

"""
"""
from vnpy_all.vnpy.trader.constant import Interval
from vnpy_all.vnpy.trader.utility import time_delta
from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from datetime import datetime


class AutomaticInvestmentStrategy(CtaTemplate):
    """"""

    author = "yuan.xin"

    period: str = "1m"  # 定投周期

    amount: int = 10  # 定投金额

    overall_investment: float = 0  # 累计定投金额
    last_invest_time: str = None  # 上一次定投时间
    next_invest_time: str = None  # 下一次定投时间

    parameters = ["period", "amount"]  # 策略参数
    variables = ["overall_investment", "last_invest_time", "next_invest_time"]  # 累计定投金额，上一次定投时间，下一次定投时间

    def on_init(self) -> None:
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        if self.period == "1m":
            interval = Interval.MINUTE
        elif self.period == "1h":
            interval = Interval.HOUR
        elif self.period == "1d":
            interval = Interval.DAILY
        elif self.period == "1w":
            interval = Interval.WEEKLY
        elif self.period == "1M":
            interval = Interval.MONTHLY
        else:
            interval = Interval.MINUTE

        self.bg: BarGenerator = BarGenerator(
            self.on_bar,  # 回调函数
            interval = interval,  # K线周期
        )
        self.am: ArrayManager = ArrayManager(size=1)

        self.load_bar(10)

    def on_start(self) -> None:
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self) -> None:
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_tick(self, tick: TickData) -> None:
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)
        print(f"{datetime.now()} new tick: {str(tick)}")

    def on_bar(self, bar: BarData) -> None:
        """
        Callback of new bar data update.
        """
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 由于K线图是按照定投周期生成，因此此函数一旦调用，则表示已经到了定投时间
        buy_amount = max(self.amount // bar.close_price, 1)  # 如果定投金额小于当前K线收盘价，则买入1手
        self.buy(bar.close_price, buy_amount)  # 开多仓买入
        self.overall_investment += buy_amount * bar.close_price  # 累计定投金额
        self.last_invest_time = bar.datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.next_invest_time = time_delta(bar.datetime, self.period).strftime("%Y-%m-%d %H:%M:%S")
        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData) -> None:
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        Callback of stop order update.
        """
        pass
