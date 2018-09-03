class DataExtractor:

    empty_cell_value = '[]'

    common_fields = [
        ('User ID', 'userID', ),
        ('Session ID', 'sessionId', ),
    ]

    values = {}

    def all_fields(self):
        """Combine the common fields with the type-specific fields"""
        return self.common_fields + self.fields

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
            value = row.get_keypath_value(keypath)
            self.values[column_name] = value

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
        return self.to_list(self.values)

    def to_list(self, values):
        """Return a list of row values ordered by column"""
        values_list = []
        print('-->VALUES', values)
        for column_name in self.column_names():
            value = self.empty_cell_value
            if column_name in values:
                value = values[column_name]
                if value is None:
                    value = self.empty_cell_value
            values_list.append(value)
        return values_list

    def extracted_rows(self):
        return [self.row_values()]
