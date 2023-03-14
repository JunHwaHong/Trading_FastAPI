# Trading_FastAPI
- Clone of "Full Stack Trading App Tutorial" on Youtude Part Time Larry
- 
```
Backend : FastAPI
Database : SQLite3
Chart    : TradingView
API      : Alpaca API
Indicator: Talib
```
## ERD
![image](https://user-images.githubusercontent.com/44192730/224952389-f4bcd9ea-623d-4e72-81c8-baf4541c552e.png)


```
│  config.py                 // config file (api id, passwd..)
│  app.db                    // sqlite3 DB File
│  create_db.py              // Create Table SQL
│  drop_db.py                // Drop Table SQL
│  populate_db.py            // populate stock table
│  populate_prices.py        // populate stock_prices table
│  populate_minute_data.py
|                            // Strategies & backtest
│  bollinger_bands.py
│  opening_range_breakdown.py
│  opening_range_breakout.py
│  backtest.py
|                            // helper functions
│  helpers.py
│  timezone.py

│  main.py
│      
└─templates
       index.html
       layout.html
       orders.html
       stock_detail.html
       strategies.html
       strategy.html

```
![image](https://user-images.githubusercontent.com/44192730/224958904-635aff27-6f1c-4492-872e-83c2a7ad36d8.png)
