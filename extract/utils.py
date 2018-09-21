# import dpath


def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)


# class KeypathDict(dict):
#     """Access nested values with keypaths"""
#
#     def get_keypath_value(self, keypath):
#         return dpath.util.get(self, keypath, separator='.')
#
#     def set_keypath_value(self, keypath, value):
#         dpath.util.set(self, keypath, value, separator='.')
