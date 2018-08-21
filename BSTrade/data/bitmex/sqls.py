def select_last(table_name, count):
    q = ("SELECT * FROM {}"
         " ORDER BY 'timestamp' LIMIT {}"
         " OFFSET (SELECT COUNT(*) FROM {}) - {}").\
        format(table_name, count, table_name, count)
    return q


def ignore_insert(t_name, col_len):
    q = ("INSERT or IGNORE INTO {}"
         " VALUES ({})").format(t_name, ','.join("?" * col_len))
    return q


def get_col_names(t_name):
    return 'PRAGMA table_info({})'.format(t_name)
