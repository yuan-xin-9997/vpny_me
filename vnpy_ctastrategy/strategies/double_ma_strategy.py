"""
代码解释 https://zhuanlan.zhihu.com/p/76383301
"""
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


class DoubleMaStrategy(CtaTemplate):
    """"""

    author = "用Python的交易员"

    fast_window: int = 10
    slow_window: int = 20

    fast_ma0: float = 0.0
    fast_ma1: float = 0.0
    slow_ma0: float = 0.0
    slow_ma1: float = 0.0

    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def on_init(self) -> None:
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.bg: BarGenerator = BarGenerator(self.on_bar)
        self.am: ArrayManager = ArrayManager(size=self.slow_window)

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
        print(f"{datetime.now()} on_bar: {str(bar)}")
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
        cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

        if cross_over:  # 金叉
            print(f"{datetime.now()} 金叉出现: fast_ma0={self.fast_ma0} slow_ma0={self.slow_ma0} fast_ma1={self.fast_ma1} slow_ma1={self.slow_ma1} bar.datetime={bar.datetime}")
            print(f"当前持仓: {self.pos}")
            if self.pos == 0:  # 持仓为0
                self.buy(bar.close_price, 1)  # 开仓买入
            elif self.pos < 0:  # 持有空仓
                self.cover(bar.close_price, 1)  # 平空仓
                self.buy(bar.close_price, 1)  # 开多仓买入

        elif cross_below:  # 死叉
            print(f"{datetime.now()} 死叉出现: fast_ma0={self.fast_ma0} slow_ma0={self.slow_ma0} fast_ma1={self.fast_ma1} slow_ma1={self.slow_ma1} bar.datetime={bar.datetime}")
            print(f"当前持仓: {self.pos}")
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
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        Callback of stop order update.
        """
        print(f"{datetime.now()} on stop_order: {str(stop_order)}")
