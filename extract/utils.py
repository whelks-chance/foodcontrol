def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)
