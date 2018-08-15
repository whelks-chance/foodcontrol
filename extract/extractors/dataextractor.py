import dpath


class DataExtractor:

    common_fields = [
        ('User ID', 'userID', ),
        ('Session ID', 'sessionId', ),
    ]

    values = {}

    def all_fields(self):
        """Combine the common fields with the type-specific fields"""
        return self.common_fields + self.fields

    def process(self, row):
        if self.can_process_row(row):
            self.extract(row)
            self.check(row)
            self.calculate(row)
            return True
        else:
            return False

    def can_process_row(self, row):
        """Return True if the row type matches the type this data extractor can process"""
        return row['type'] == self.__class__.type

    def clear(self):
        """Reset common value and calculation stores. Override to to reset type-specific value and calculation stores"""
        self.values.clear()

    def extract(self, row):
        """Store the column value for each keypath"""
        self.clear()
        for column_name, keypath in self.all_fields():
            value = self.value(row, keypath)
            self.values[column_name] = value

    @staticmethod
    def value(json_object, keypath):
        """Access nested dictionary values with a dot-separated string of keys"""
        return dpath.util.get(json_object, keypath, separator='.')

    def check(self, row):
        """Override to perform type-specific row checks"""
        pass

    def calculate(self, row):
        """Override to perform type-specific row calculations"""
        pass

    def column_names(self):
        """Return a list of column names"""
        return [column_name for column_name, _ in self.all_fields()]

    def row_values(self):
        """Return a list of row values. Missing data or None values are blank ''"""
        values = []
        empty_cell_value = ''
        for column_name, _ in self.all_fields():
            value = empty_cell_value
            if column_name in self.values:
                value = self.values[column_name]
                if value is None:
                    value = empty_cell_value
            values.append(value)
        return values
