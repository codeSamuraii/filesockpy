from functools import cache


@cache
def cached_range(start, stop, step):
    return range(start, stop, step)