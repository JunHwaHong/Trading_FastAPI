import sqlite3
import config
import alpaca_trade_api as tradeapi
from datetime import date, datetime
import FinanceDataReader as fdr
from timezone import is_dst
from talib import MA_Type
import numpy as np
import talib

print(datetime.now())

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = 'bollinger_bands'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy ON stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]

current_date = '2020-10-29'
# currnet_date = date.today().isoformat()

start_minute_bar = f"{current_date} 09:30:00-05:00"
end_minute_bar = f"{current_date} 10:28:00-05:00"

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

orders = api.list_orders(status='all', limit=500, after=current_date)
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']

messages = []

for symbol in symbols:


    # day_bars = fdr.DataReader(symbol, '2020-10-01', '2020-11-01')
    # opening_range_low = day_bars['Low'].min()
    # opening_range_high = day_bars['High'].max()
    # opening_range = opening_range_high - opening_range_low
    #######
    minute_bars = api.polygon.historic_agg_v2(symbol, 1, 'minute', _from=current_date, to=current_date).df
    
    market_open_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    market_open_bars = minute_bars.loc[market_open_mask]

    if len(market_open_bars) >= 20:
        closes = market_open_bars.close.values
        upper, middle, lower = talib.BBANDS(closes, 20, 2, matype=MA_Type.T3)
        
        current_candle = market_open_bars.iloc[-1]
        previous_candle = market_open_bars.iloc[-2]
        
        if current_candle.close < lower[-1] and previous_candle.close < lower[-2]:
            print(f"{symbol} closed above lower bollinger band")

            if symbol not in existing_order_symbols:
                limit_price = after_opening_range_breakdown.iloc[0]['close']
                limit_price = current_candle.close

                candle_range = current_candle.high - current_candle.low
                print(f"placing order for {symbol} at {limit_price}")

                try:
                    api.submit_order(
                        symbol=symbol,
                        side='buy',
                        type='limit',
                        qty='100',
                        time_in_force='day',
                        order_class='bracket',
                        limit_price=limit_price,
                        take_profit=dict(
                            limit_price=limit_price + (candle_range * 3),
                        ),
                        stop_loss=dict(
                            stop_price=previous_candle.low,
                        )
                    )
                except Exception as e:
                    print(f"could not submit order {e}")
            else:
                print(f"Already an order for {symbol}, skipping")
            

    opening_range_mask= (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]

    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    after_opening_range_breakdown = after_opening_range_bars[after_opening_range_bars['close'] < opening_range_low]

    if not after_opening_range_breakdown.empty:
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakdown.iloc[0]['close']

            messages.append(f"selling short {symbol} at {limit_price}, closed_below {opening_range_low}\n\n{after_opening_range_breakdown.iloc[0]}\n\n")

            print(f"selling short {symbol} at {limit_price}, closed_below {opening_range_low} at {after_opening_range_breakdown.iloc[0]}")

            try:
                api.submit_order(
                    symbol=symbol,
                    side='sell',
                    type='limit',
                    qty='100',
                    time_in_force='day',
                    order_class='bracket',
                    limit_price=limit_price,
                    take_profit=dict(
                        limit_price=limit_price - opening_range,
                    ),
                    stop_loss=dict(
                        stop_price=limit_price + opening_range,
                    )
                )
            except Exception as e:
                print(f"could not submit order {e}")
        else:
            print(f"Already an order for {symbol}, skipping")

print(messages)
with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
    email_message += "\n\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)
