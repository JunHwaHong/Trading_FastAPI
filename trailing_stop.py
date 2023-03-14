import config
import alpaca_trade_api as tradeapi
import numpy as np
import talib

from helpers import calculate_quantity

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

symbols = ['SPY', 'IWM', 'DIA']

# for symbol in symbols:
#     quote = api.get_latest_quote(symbol)

#     api.submit_order(
#         symbol=symbol,
#         side='buy',
#         type='market',
#         qty=calculate_quantity(quote.bidprice),
#         time_in_force='day'
#     )

# orders = api.list_orders()
# positions = api.list_positions()

# api.submit_order(
#         symbol='IWM',
#         side='sell',
#         qty=57,
#         time_in_force='day',
#         type='trailing_stop',
#         trail_price='0.20'
#     )


daily_bars = api.polygon.historic_agg_v2('NIO', 1, 'day', _from='2020-10-01', to='2020-11-13')

atr = talib.ATR(daily_bars.high.values, daily_bars.low.values, daily_bars.close.values, timeperiod=14)