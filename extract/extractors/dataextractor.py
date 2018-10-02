import dpath
from keypath_extractor import KeypathExtractor


class DataExtractor:
    """The abstract base class for all game and question data extractors"""

    # This value is used to represent any kind of missing, blank or null value
    EMPTY_CELL_VALUE = '[]'

    def get_extractor_type(self):
        """Return the type of game or question this extractor can process"""
        return self.type

    def get_filename(self):
        return self.get_extractor_type()

    def get_common_keypaths(self):
        """Return a list of keypaths that are common to all rows"""
        return [
            ('userID', 'User ID'),
            ('sessionId', 'Session ID'),
        ]

    def get_value_keypaths(self):
        """Return a list of keypaths specific to this data extractor"""
        return []

    def get_derived_value_keypaths(self):
        """Return a list of keypaths that derive values from values extracted by this data extractor"""
        return []

    def get_all_column_keypaths(self):
        """
        Return a list that combines the column names of the common,
        value and derived value keypaths for this data extractor
        """
        return\
            self.get_common_keypaths() + \
            self.get_value_keypaths_for_naming_columns() + \
            self.get_derived_value_keypaths()

    def get_value_keypaths_for_naming_columns(self):
        """
        Subclasses may generate multiple CSV rows per JSON row but
        we only need the column names for the first set of keypaths.
        """
        keypaths = self.get_value_keypaths()
        if self.keypaths_are_nested(keypaths):
            keypaths = keypaths[0]
        return keypaths

    @staticmethod
    def keypaths_are_nested(keypaths):
        return type(keypaths[0]) is list

    def get_column_names(self):
        """
        Return a combined list of column names for the common,
        value and derived value keypaths for this data extractor
        """
        # A keypath is a 3-element tuple: (source keypath, destination keypath, transformer function)
        # The destination keypath is used as the column name
        return [keypath[1] for keypath in self.get_all_column_keypaths()]

    def get_csv_row_values(self, values):
        return self.listify_values(self.get_column_names(), values)

    @staticmethod
    def listify_values(column_names, values):
        """Return a list of column values in the same order as the corresponding column name"""
        values_list = []
        for column_name in column_names:
            value = DataExtractor.EMPTY_CELL_VALUE
            if column_name in values:
                value = values[column_name]
                if value == '' or value is None:
                    value = DataExtractor.EMPTY_CELL_VALUE
            values_list.append(value)
        return values_list

    def process_row(self, row):
        """
        Attempt to process a row. Return True if this data extractor can
        process this type of row and the row represents a completed session
        """
        if self.can_process_row(row):
            if self.session_is_complete(row):
                self.extract_row_data(row)
                return True
        else:
            return False

    def can_process_row(self, row):
        """Return True if the row type matches the type this data extractor can process"""
        return row['type'] == self.get_extractor_type()

    def session_is_complete(self, row):
        """Return True if the row represents a completed session; False otherwise"""

        def get_session_state(row):
            """
            Handle inconsistently formatted data structures:
            data -> object vs data -> [ object ]
            """
            session_state = 'COMPLETE'
            try:
                session_state = self.get_keypath_value(row, 'data.0.sessionState')
            except KeyError:
                try:
                    session_state = self.get_keypath_value(row, 'data.sessionState')
                except KeyError:
                    # There is no sessionState key for this row it is implicitly complete
                    pass
            finally:
                return session_state

        return get_session_state(row) == 'COMPLETE'

    def extract_row_data(self, row):
        """Override to perform extractor-specific extraction"""
        pass

    def extract_values(self, data):
        """Extract values from a data dictionary using the keypaths of this data extractor"""
        value_keypaths = self.get_common_keypaths() + self.get_value_keypaths()
        derived_value_keypaths = self.get_derived_value_keypaths()
        values = self.extract_values_with_keypaths(value_keypaths, derived_value_keypaths, data)
        return [values]

    @staticmethod
    def extract_values_with_keypaths(value_keypaths, derived_value_keypaths, data):
        """Extract values from a data dictionary using the keypaths of this data extractor"""
        values = {}
        try:
            values = KeypathExtractor(value_keypaths).extract(data)
            values = KeypathExtractor(derived_value_keypaths).extract(values, values)
        except KeyError:
            # There are cases where generated keypaths do not occur so ignore this exception
            pass
        except ValueError as e:
            print("ValueError: ", e)
        finally:
            return values

    def extracted_rows(self):
        """Return a list of one (games) or more (questions) rows of data for output to CSV"""
        rows = []
        for rv in self.csv_rows:
            row = self.listify_values(self.get_column_names(), rv)
            if not self.row_contains_all_empty_values(row):
                rows.append(row)
        return rows

    @staticmethod
    def row_contains_all_empty_values(row):
        # The
        for item in row[:-2]:
            if item is not DataExtractor.EMPTY_CELL_VALUE:
                return False
        return True

    @staticmethod
    def get_keypath_value(dictionary, keypath):
        """Return the value of a dictionary at a keypath"""
        return dpath.util.get(dictionary, keypath, separator='.')
