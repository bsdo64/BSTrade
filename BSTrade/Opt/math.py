import numpy as np
from numba import jit, int64, float64


@jit(int64(int64, int64, int64), cache=True, fastmath=True)
def cache_x_range(num1, num2, num3):
    return (num1 + num2) // num3


@jit(int64(int64, int64), cache=True, fastmath=True)
def cache_x_pos(num1, num2):
    return num1 // num2


@jit(float64(int64, float64[:], float64[:]), cache=True, fastmath=True)
def cache_scale_y(height, s1, s2):
    return height / nb_max_min(s1, s2)


@jit(float64(int64, int64), cache=True, fastmath=True)
def cache_scale_x(width, s1):
    return width / s1


@jit(float64(float64[:], float64[:]), cache=True, fastmath=True)
def nb_max_min(s1, s2):
    return np.max(s1) - np.min(s2)


@jit(float64(int64, int64, float64), cache=True, fastmath=True)
def price_from_id(idx, id_int, tick_size):
    return (idx * 1e8 - id_int) * tick_size


@jit(float64(int64, float64, float64), cache=True, fastmath=True)
def id_from_price(idx, price, tick_size):
    return idx * 1e8 - price / tick_size
