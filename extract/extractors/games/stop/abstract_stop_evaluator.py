class AbstractStopEvaluator:

    def evaluate(self, row):
        pass

    def populate_spreadsheet(self, spreadsheet):
        pass

    def has_session_log_entries(self):
        if hasattr(self, 'session_event_log'):
            return self.session_event_log.is_empty()
        return False
