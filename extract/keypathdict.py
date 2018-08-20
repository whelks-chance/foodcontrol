import dpath


class KeypathDict(dict):

    def get_keypath_value(self, keypath):
        return dpath.util.get(self, keypath, separator='.')

    def set_keypath_value(self, keypath, value):
        pass
