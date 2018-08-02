from numba import vectorize, int64, float64


@vectorize([int64(int64, float64)], fastmath=True, cache=True)
def to_time_axis(s, v):
    return s / 10 ** 9 / v


@vectorize([int64(int64, int64)], fastmath=True, cache=True)
def to_time_scale(series, val):
    return series * val


@vectorize([int64(int64, float64)], fastmath=True, cache=True)
def make_r_data(val, series):
    return val - series
