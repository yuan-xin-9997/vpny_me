#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time: 2025/05/12 21:22
# @Author: yuan.xin
# @FileName: high_throw_bar_gain_hunting_strategy.py
# @Description: 高抛低吸策略

from datetime import datetime
import numpy as np
from vnpy_all.vnpy.trader.utility import split_list, is_monotonic_increasing, is_monotonic_decreasing
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
from vnpy_all.vnpy.trader.constant import Interval, Direction


class HighThrowBarGainHuntingStrategy(CtaTemplate):
    """HighThrowBarGainHuntingStrategy"""

    author = "yuan.xin"

    # 策略参数
    interval = "1m"      # 粒度
    window = 10          # 窗口大小，单位：interval
    budget = 10          # 本次策略运行的预算，单位：份（期货，1份=1手，股票，1份=100股）
    stop_loss_ratio: float = 0.1  # 止损比例
    take_profit_ratio: float = 0.2  # 止盈比例
    control_factor: float = 0.8   # 控制因子，控制买入时机和卖出时机，取值范围0.5-0.99，如果不在这个范围内，则默认0.8

    # 策略变量
    overall_investment: float = 0  # 累计投入金额
    last_invest_time: str = None  # 上一次交易时间
    used_budget: int = 0  # 已经使用的预算，单位：份
    current_profit: float = 0  # 当前收益
    current_profit_rate: float = 0  # 当前收益率

    parameters = ["interval", "window", "budget", "stop_loss_ratio", "take_profit_ratio", "control_factor"]
    variables = ["overall_investment", "last_invest_time", "used_budget", "current_profit", "current_profit_rate"]

    def on_init(self) -> None:
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        # self.bg: BarGenerator = BarGenerator(self.on_bar)
        # self.am: ArrayManager = ArrayManager()

        if self.interval == "1m":
            interval = Interval.MINUTE
            days = 1
        elif self.interval == "1h":
            interval = Interval.HOUR
            days = 1
        elif self.interval == "1d":
            interval = Interval.DAILY
            days = self.window
        elif self.interval == "1w":
            interval = Interval.WEEKLY
            days = self.window * 7
        elif self.interval == "1M":
            interval = Interval.MONTHLY
            days = self.window * 30
        else:
            interval = Interval.MINUTE
            days = 1

        self.bg: BarGenerator = BarGenerator(
            self.on_bar,  # 回调函数
            interval = interval,  # K线周期
        )
        self.am: ArrayManager = ArrayManager(size=self.window)  # size 列表长度

        # 规整control_factor
        if self.control_factor < 0.5 or self.control_factor > 0.99:
            self.control_factor = 0.8

        self.load_bar(days=days)  # 加载历史数据

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
        print(f"{datetime.now()} on_bar: {str(bar)}")
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:  # 策略是否初始化
            return

        if self.trading == False:  # 策略是否启动
            return

        # 止盈策略判断
        # 收益率大于等于止盈比例，且持仓>0，且持仓数量已经超过30%
        if self.pos > 0 and self.pos / self.budget >= 0.3:
            if self.current_profit_rate >= self.take_profit_ratio:
                self.sell(bar.close_price, self.pos // 2)  # 平仓卖出，假设每次平仓一半
                self.put_event()
                return

            # 止损策略判断
            # 收益率小于等于止损比例，且持仓>0，且持仓数量已经超过30%
            if self.current_profit_rate <= -self.stop_loss_ratio:
                self.sell(bar.close_price, self.pos // 2)  # 平仓卖出，假设每次平仓一半
                return

        # 高抛低吸策略判断
        if self.used_budget < self.budget:
            front, rear = split_list(am.close_array, self.control_factor)
            # 判断买入时机
            #   （1）在window的前control_factor阶段按照收盘价为单调递减，在后1-control_factor阶段按照收盘价为单调递增
            # buy_time_flag = is_monotonic_decreasing(front) and is_monotonic_increasing(rear)
            # sell_time_flag = is_monotonic_increasing(front) and is_monotonic_increasing(rear)
            #    或
            #   （2）在window的前control_factor阶段按照收盘价拟合的曲线，斜率<=-0.6，在后1-control_factor阶段按照收盘价拟合曲线，斜率>=0.6
            front_slope = np.polyfit([i for i in range(len(front))], front, 1)[0]
            rear_slope  = np.polyfit([i for i in range(len(rear))], rear, 1)[0]
            buy_time_flag = front_slope <= -0.6 and rear_slope >= 0.6
            sell_time_flag = front_slope >= 0.6 and rear_slope <= -0.6
            if buy_time_flag:
                if self.pos == 0:  # 持仓为0
                    self.buy(bar.close_price, 1)  # 开仓买入
                elif self.pos < 0:  # 持有空仓
                    self.cover(bar.close_price, 1)  # 平空仓
                    self.buy(bar.close_price, 1)  # 开多仓买入

                self.put_event()

            # 判断卖出时机
            #   （1）在window的前control_factor阶段按照收盘价为单调递增加，在后1-control_factor阶段按照收盘价为单调递增
            #    或
            #   （2）在window的前control_factor阶段按照收盘价拟合的曲线，斜率>=0.6，在后1-control_factor阶段按照收盘价拟合曲线，斜率=<-0.6
            if sell_time_flag:
                if self.pos == 0:  # 持仓为0
                    self.short(bar.close_price, 1)
                elif self.pos > 0:  # 持有多仓
                    self.sell(bar.close_price, 1)  # 卖出
                    self.short(bar.close_price, 1)  # 开空仓卖出

                self.put_event()


    def on_order(self, order: OrderData) -> None:
        """
        Callback of new order data update.
        """
        print(f"{datetime.now()} on order: {str(order)}")

    def on_trade(self, trade: TradeData) -> None:
        """
        Callback of new trade data update.
        """
        print(f"{datetime.now()} on trade: {str(trade)}")
        self.used_budget = abs(self.pos)  # 使用的预算等于持仓数量

        self.last_invest_time = trade.datetime.strftime("%Y-%m-%d %H:%M:%S")  # 上一次交易时间
        # 交易方向
        if trade.direction.value == Direction.LONG.value:
            self.overall_investment += trade.price * trade.volume  # 累计投入金额

        elif trade.direction.value == Direction.SHORT.value:
            self.overall_investment -= trade.price * trade.volume  # 累计投入金额
        else:
            print(f"{datetime.now()} on_trade: {str(trade.direction)}")
            self.overall_investment += trade.price * trade.volume  # 累计投入金额

        # 计算收益和收益率
        self.current_profit = self.overall_investment - self.pos * trade.price
        try:
            self.current_profit_rate = self.current_profit / self.overall_investment
        except ZeroDivisionError:
            self.current_profit_rate = 0
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        Callback of stop order update.
        """
        print(f"{datetime.now()} on stop_order: {str(stop_order)}")
