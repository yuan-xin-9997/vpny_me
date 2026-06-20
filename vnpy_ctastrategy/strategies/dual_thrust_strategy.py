from datetime import time
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


class DualThrustStrategy(CtaTemplate):
    """
    Dual Thrust是一个经典的日内突破交易策略，它通过计算前一个交易日的价格波动范围来确定当日的入场和出场阈值。
    ref:  https://xueqiu.com/8346773006/295868650

    """

    author = "用Python的交易员"

    # 策略参数
    fixed_size: int = 1  # 每次交易的数量
    k1: float = 0.4      # 上轨因子
    k2: float = 0.6      # 下轨因子

    # 策略期间使用的变量
    day_open: float = 0
    day_high: float = 0  # 当日最高价
    day_low: float = 0   # 当日最低价
    
    day_range: float = 0
    long_entry: float = 0   # 上轨
    short_entry: float = 0  # 下轨
    long_entered: bool = False
    short_entered: bool = False

    parameters = ["k1", "k2", "fixed_size"]
    variables = ["day_range", "long_entry", "short_entry"]

    def on_init(self) -> None:
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.bg: BarGenerator = BarGenerator(self.on_bar)  # BarGenerator 生成K线，默认间隔是 Interval.MINUTE
        self.am: ArrayManager = ArrayManager()  # ArrayManager K线列表管理器，默认长度是size: int = 100

        self.bars: list[BarData] = []
        self.exit_time: time = time(hour=14, minute=55)  # todo 退出时间？？？有什么作用

        self.load_bar(10)  # 加载历史数据，默认是10天的K线，从当前时间倒推10天的历史数据，或从回测策略指定的开始时间前10天的数据,todo 作用是啥？

    def on_start(self) -> None:
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """
        Callback of new bar data update.
        """
        self.cancel_all()
        # todo 不明白这里pop，又是-2的逻辑是什么意思
        self.bars.append(bar)
        if len(self.bars) <= 2:
            return
        else:
            self.bars.pop(0)  # 确保self.bars里面只有2个元素
        last_bar = self.bars[-2]  # 上一个K线

        if last_bar.datetime.date() != bar.datetime.date():  # 两个K线是否是同一天
            if self.day_high:
                self.day_range = self.day_high - self.day_low
                self.long_entry = bar.open_price + self.k1 * self.day_range
                self.short_entry = bar.open_price - self.k2 * self.day_range

            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_low = bar.low_price

            self.long_entered = False
            self.short_entered = False
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        if not self.day_range:
            return

        if bar.datetime.time() < self.exit_time:
            if self.pos == 0:
                if bar.close_price > self.day_open:
                    if not self.long_entered:
                        self.buy(self.long_entry, self.fixed_size, stop=True)
                else:
                    if not self.short_entered:
                        self.short(self.short_entry,
                                   self.fixed_size, stop=True)

            elif self.pos > 0:
                self.long_entered = True

                self.sell(self.short_entry, self.fixed_size, stop=True)

                if not self.short_entered:
                    self.short(self.short_entry, self.fixed_size, stop=True)

            elif self.pos < 0:
                self.short_entered = True

                self.cover(self.long_entry, self.fixed_size, stop=True)

                if not self.long_entered:
                    self.buy(self.long_entry, self.fixed_size, stop=True)

        else:
            if self.pos > 0:
                self.sell(bar.close_price * 0.99, abs(self.pos))
            elif self.pos < 0:
                self.cover(bar.close_price * 1.01, abs(self.pos))

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
