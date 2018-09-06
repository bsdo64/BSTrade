from peewee import Model, SqliteDatabase, TextField, AutoField, FloatField, \
    IntegerField

database = SqliteDatabase('BSTrade/Data/bitmex/bitmex.db', **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Exchange(BaseModel):
    name = TextField()

    class Meta:
        table_name = 'exchange'


class Instrument(BaseModel):
    asset = TextField(null=True)
    description = TextField(null=True)
    exchange = TextField(null=True)
    inst = IntegerField(column_name='inst_id', null=True)
    makerfee = FloatField(column_name='makerFee', null=True)
    market = TextField(null=True)
    maxorderqty = IntegerField(column_name='maxOrderQty', null=True)
    maxprice = FloatField(column_name='maxPrice', null=True)
    pairsymbol = TextField(column_name='pairSymbol', null=True)
    rootsymbol = TextField(column_name='rootSymbol', null=True)
    state = TextField(null=True)
    symbol = TextField(null=True)
    takerfee = FloatField(column_name='takerFee', null=True)
    ticksize = FloatField(column_name='tickSize', null=True)

    class Meta:
        table_name = 'instrument'


class Tradebin1M(BaseModel):
    close = FloatField()
    foreignnotional = IntegerField(column_name='foreignNotional', null=True)
    high = FloatField()
    homenotional = FloatField(column_name='homeNotional', null=True)
    lastsize = IntegerField(column_name='lastSize', null=True)
    low = FloatField()
    open = FloatField()
    symbol = TextField()
    timestamp = TextField(index=True)
    trades = IntegerField()
    turnover = IntegerField(null=True)
    volume = IntegerField()
    vwap = FloatField(null=True)

    class Meta:
        table_name = 'tradebin1m'
