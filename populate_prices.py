import sqlite3, config
import FinanceDataReader as fdr
import talib
import numpy as np

import datetime
start_str = "2022-10-01"
today = datetime.datetime.today()
yesterday = datetime.datetime.today() - datetime.timedelta(1)
today_str = today.strftime("%Y-%m-%d")

connection = sqlite3.connect(config.DB_FILE)
print(connection)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name FROM stock
""")
rows = cursor.fetchall()

symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

symbols = symbols[:20]
symbols = ['AAPL']
chunk_size = 200

for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]

    for t in symbol_chunk:
        try:
            df = fdr.DataReader(t, start_str, today_str)
            print(f"processing symbol {t}")

            stock_id = stock_dict[t]
            recent_closes = df['Close'].values
            
            for index, row in df.iterrows():
                if len(recent_closes) >= 50 and yesterday.date() == row.name.date():
                    sma_20 = talib.SMA(recent_closes, 20)[-1]
                    sma_50 = talib.SMA(recent_closes, 50)[-1]
                    rsi_14 = talib.RSI(recent_closes, 14)[-1]
                else:
                    sma_20, sma_50, rsi_14 = None, None, None

                cursor.execute("""
                    INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (stock_id, row.name.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], sma_20, sma_50, rsi_14))
        except Exception as e:
            print(e)

connection.commit()