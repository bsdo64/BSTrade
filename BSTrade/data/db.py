import numpy

import pandas
import sqlite3
import ciso8601

con = sqlite3.connect("BSTrade.db")
cursor = con.cursor()

df = pandas.read_pickle('bitmex_1m_2018.pkl')
df.to_sql('bitmex_trade_bucket', con, if_exists='replace', index=False)

df2 = pandas.read_sql("SELECT t.* FROM bitmex_trade_bucket t", con)

df2['timestamp'] = df2['timestamp'].astype('datetime64')

v = df2['timestamp'].diff().astype(numpy.int64)
v2 = v[v != 60000000000]
print(v2)


rng = pandas.date_range('01-01-2018', periods=len(df2['timestamp']), freq='min')
v = rng.difference(df2['timestamp']).format()
print(v)