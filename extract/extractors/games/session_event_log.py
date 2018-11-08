class SessionEventLog:

    def __init__(self):
        self.logs = []

    def clear(self):
        self.logs = []

    def log_message(self, message, data=None):
        log = {
            'message': message,
            'data': data
        }
        self.logs.append(log)

    def log_message_if_check_failed(self, check_result, session_event, extra_message=None):
        if not check_result:
            message = 'Check failed: trialType={} gameSessionID={} roundID={}, trialID={}'.format(
                                session_event['trialType'],
                                session_event['gameSessionID'],
                                session_event['roundID'],
                                session_event['trialID'])
            if extra_message:
                message = ' ({})'.format(extra_message)
            self.log_message(message, session_event)

    def print(self):
        print('\nLOGS:')
        for log in self.logs:
            print('\t', log['message'])
