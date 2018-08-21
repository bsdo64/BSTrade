import time

import numpy

import pandas
import sqlite3
import ciso8601

conn = sqlite3.connect("bitmex.db")
c = conn.cursor()

# Create table
# c.execute('''CREATE TABLE stocks
#              (date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Save (commit) the changes
# conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.

s = time.perf_counter_ns()
symbol = 'XBTUSD'
count = 500
c.execute("SELECT * FROM tradebin1m"
          " ORDER BY timestamp"
          " LIMIT ?"
          " OFFSET (SELECT COUNT(*) FROM tradebin1m) - ?"
          , [count, count]
          )
print('execute : ', (time.perf_counter_ns() - s) / 1000_000)

s = time.perf_counter_ns()
d = c.fetchall()
print('fetchall : ', (time.perf_counter_ns() - s) / 1000_000)
print(d)


s = time.perf_counter_ns()
# Larger example that inserts many records at a time
c.executemany("INSERT or IGNORE INTO bitmex_trade_bucket"
              " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", d)
print('execute many : ', (time.perf_counter_ns() - s) / 1000_000)

s = time.perf_counter_ns()
c.execute("SELECT * FROM tradebin1m"
          " ORDER BY timestamp"
          " LIMIT ?"
          " OFFSET (SELECT COUNT(*) FROM tradebin1m) - ?"
          , [count, count]
          )
print('execute : ', (time.perf_counter_ns() - s) / 1000_000)

s = time.perf_counter_ns()
d = c.fetchall()
print('fetchall : ', (time.perf_counter_ns() - s) / 1000_000)
print(d)


conn.close()
