
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/05/12 18:42
# @Author  : yuan.xin
# @FileName: download_rq_data.py
# @Description:
from datetime import datetime
from vnpy.trader.object import BarData, TickData, HistoryRequest
from vnpy.trader.constant import Direction, Exchange, Interval, Offset, Status, Product, OptionType, OrderType
from vnpy_rqdata.rqdata_datafeed import RqdataDatafeed

if __name__ == '__main__':
    rq = RqdataDatafeed()
    rq.init()
    req: HistoryRequest = HistoryRequest(
        symbol="au2508",
        exchange=Exchange.SHFE,
        interval=Interval("1m"),
        start=datetime(2025, 5, 12, 9, 00, 00),
        end=datetime(2025, 5, 12, 9, 10, 00)
    )
    res = rq.query_tick_history(
        req,

    )
    print(res)
    print("done")
