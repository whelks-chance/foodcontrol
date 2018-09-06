class DataExtractor:

    empty_cell_value = '[]'

    common_values = {}
    values = {}

    def name(self):
        return self.type

    @staticmethod
    def common_fields():
        return [
            ('User ID', 'userID', ),
            ('Session ID', 'sessionId', ),
        ]

    def _fields(self):
        return self.fields

    def clear(self):
        """Reset common value and calculation stores. Override to to reset type-specific value and calculation stores"""
        self.values.clear()

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
                self.extract_common_field_values(row)
                self.extract(row)
                self.check(row)
                self.calculate(row)
                return True
        else:
            return False

    def can_process_row(self, row):
        """Return True if the row type matches the type this data extractor can process"""
        return row['type'] == self.__class__.type

    def extract(self, row):
        self.values = {}
        self.extract_field_values(self._fields(), row, self.values)

    def extract_common_field_values(self, row):
        self.common_values = {}
        print(self.common_fields())
        self.extract_field_values(self.common_fields(), row, self.common_values)

    @staticmethod
    def extract_field_values(fields, row, values):
        for column_name, keypath in fields:
            try:
                value = row.get_keypath_value(keypath)
                values[column_name] = value
            except KeyError as e:
                print('KeyError', e)

    def calculate_derived_field_values(self, values):
        """Derive new values from extracted field values"""
        if hasattr(self, 'derived_fields'):
            for source_column_name, destination_column_name, code_function_name in self.derived_fields:
                value_derivation_fn = getattr(self, code_function_name)
                if source_column_name:
                    try:
                        value = values[source_column_name]
                    except KeyError as e:
                        print('\ncalculate_derived_field_values():')
                        print(e)
                        print(values)
                else:
                    value = values
                derived_value = DataExtractor.empty_cell_value
                if value and value != DataExtractor.empty_cell_value:
                    derived_value = value_derivation_fn(value)
                values[destination_column_name] = derived_value

    def check(self, row):
        """Override to perform type-specific row checks"""
        pass

    def calculate(self, row):
        """Override to perform type-specific row calculations"""
        pass

    def all_column_names(self):
        return self.common_column_names() + self.column_names()

    def common_column_names(self):
        return [column_name for column_name, _ in self.common_fields()]

    def column_names(self):
        """Return a list of column names"""
        # Standard column names
        column_names = [column_name for column_name, _ in self._fields()]
        # Derived column names (if any)
        if hasattr(self, 'derived_fields'):
            for _, derived_column_name, _ in self.derived_fields:
                column_names.append(derived_column_name)
        return column_names

    def all_row_values(self):
        return self.common_row_values() + self.row_values()

    def common_row_values(self):
        return self.to_list(self.common_column_names(), self.common_values)

    def row_values(self):
        return self.to_list(self.column_names(), self.values)

    @staticmethod
    def to_list(column_names, values):
        """Return a list of column values in the same order as the corresponding column name"""
        values_list = []
        for column_name in column_names:
            value = DataExtractor.empty_cell_value
            if column_name in values:
                value = values[column_name]
                if value is None:
                    value = DataExtractor.empty_cell_value
            values_list.append(value)
        return values_list

    def extracted_rows(self):
        return [self.all_row_values()]


