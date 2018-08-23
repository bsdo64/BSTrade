def select_last(table_name, count, with_id=False):
    q = ("SELECT * FROM {}"
         " ORDER BY 'timestamp' LIMIT {}"
         " OFFSET (SELECT COUNT(*) FROM {}) - {}").\
        format(table_name, count, table_name, count)
    return q


def ignore_insert(t_name, keys: list):
    col_len = len(keys)

    q = ("INSERT or IGNORE INTO {}"
         " ({})"
         " VALUES ({})").format(t_name,
                                ','.join(keys),
                                ','.join("?" * col_len))
    return q


def get_col_names(t_name):
    return 'PRAGMA table_info({})'.format(t_name)


def create_table(t_name):
    if t_name == 'tradebin1m':
        q = """
        CREATE TABLE IF NOT EXISTS tradebin1m
        (
            id INTEGER PRIMARY KEY,
            timestamp text NOT NULL,
            symbol text NOT NULL,
            open real NOT NULL,
            high real NOT NULL,
            low real NOT NULL,
            close real NOT NULL,
            trades integer NOT NULL,
            volume integer NOT NULL,
            vwap real,
            lastSize integer,
            turnover integer,
            homeNotional real,
            foreignNotional integer
        );
        """

    elif t_name == 'symbol':
        q = """
        CREATE TABLE IF NOT EXISTS symbol
        (
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            type TEXT NOT NULL,
            code TEXT,
            provider TEXT,
            description TEXT
        );
        """

    else:
        q = ""

    return q


def create_index(t_name, col_name, uniq=False):
    q = """
        CREATE {} INDEX IF NOT EXISTS {}_{}_uindex 
        ON {} ({});
    """.format("UNIQUE" if uniq else "",
               t_name,
               col_name,
               t_name,
               col_name)

    return q
