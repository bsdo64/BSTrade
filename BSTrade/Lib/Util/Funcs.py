import random

uid_chars = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
    '5', '6', '7', '8', '9', '0'
)


def short_uid(length=4):
    count = len(uid_chars) - 1
    c = ''
    for i in range(0, length):
        c += uid_chars[random.randint(0, count)]
    return c
