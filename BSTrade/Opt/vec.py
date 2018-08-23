from numba import vectorize, int64, float64


@vectorize([int64(int64, float64)], fastmath=True, cache=True)
def ts_to_axis(s, v):
    # marker = timestamp - 1 min
    return s / 10 ** 9 / v - 1


@vectorize([int64(int64, int64)], fastmath=True, cache=True)
def to_time_scale(series, val):
    return series * val


@vectorize([int64(int64, float64)], fastmath=True, cache=True)
def make_r_data(val, series):
    return val - series


@vectorize([int64(int64, int64)], fastmath=True, cache=True)
def mult(series, val):
    return series * val


@vectorize([int64(int64, float64)], fastmath=True, cache=True)
def sub(val, series):
    return val - series
