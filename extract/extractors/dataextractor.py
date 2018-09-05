class DataExtractor:

    empty_cell_value = '[]'

    common_values = {}
    values = {}

    def name(self):
        return self.type

    @staticmethod
    def common_fields():
        print('DataExtractor.common_fields()')
        return [
            ('User ID', 'userID', ),
            ('Session ID', 'sessionId', ),
        ]

    def _fields(self):
        return self.fields

    @staticmethod
    def session_is_complete(row):
        session_state = 'COMPLETE'
        # Handle inconsistently formatted data structures between games:
        # data -> object vs data -> [ object ]
        try:
            session_state = row.get_keypath_value('data.0.sessionState')
        except KeyError:
            try:
                session_state = row.get_keypath_value('data.sessionState')
            except KeyError:
                # There is no sessionState for this row so it is implicitly complete
                pass
        finally:
            return session_state == 'COMPLETE'

    def process(self, row):
        if self.can_process_row(row):
            if self.session_is_complete(row):
                self.extract_common_values(row)
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

    @staticmethod
    def extract_fields(fields, values, row):
        print('fields:', fields)
        for column_name, keypath in fields:
            value = row.get_keypath_value(keypath)
            values[column_name] = value

    def extract_common_values(self, row):
        """Store the common column values"""
        self.common_values = {}
        print(self.common_fields())
        self.extract_fields(self.common_fields(), self.common_values, row)

    def extract(self, row):
        """Store the column value for each keypath"""
        self.clear()
        self.extract_fields(self._fields(), self.values, row)

    def check(self, row):
        """Override to perform type-specific row checks"""
        pass

    def calculate(self, row):
        """Override to perform type-specific row calculations"""
        pass

    def common_column_names(self):
        """Return a list of the common column names"""
        return [column_name for column_name, _ in self.common_fields()]

    def column_names(self):
        """Return a list of column names"""
        return [column_name for column_name, _ in self._fields()]

    def all_column_names(self):
        return self.common_column_names() + self.column_names()

    def common_row_values(self):
        return self.to_list(self.common_column_names(), self.common_values)

    def row_values(self):
        return self.to_list(self.column_names(), self.values)

    def all_row_values(self):
        return self.common_row_values() + self.row_values()

    def to_list(self, column_names, values):
        """Return a list of row values ordered by column"""
        values_list = []
        print('-->VALUES', values)
        for column_name in column_names:
            value = self.empty_cell_value
            if column_name in values:
                value = values[column_name]
                if value is None:
                    value = self.empty_cell_value
            values_list.append(value)
        return values_list

    def extracted_rows(self):
        return [self.all_row_values()]
