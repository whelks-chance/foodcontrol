import dpath
import logging
import statistics


def irange(start, end):
    """Return a range that includes the end value: 1,5 -> 1...5 rather than 1...4"""
    return range(start, end + 1)


def get_session_events(row):
    """
    Handle inconsistently formatted data structures:
    data -> object vs data -> [ object ]
    """
    session_events = None
    try:
        session_events = get_keypath_value(row, 'data.0.sessionEvents')
    except KeyError:
        try:
            session_events = get_keypath_value(row, 'data.sessionEvents')
        except KeyError:
            pass
    return session_events


def get_keypath_value(dictionary, keypath):
    """Return the value of a dictionary at a keypath"""
    return dpath.util.get(dictionary, keypath, separator='.')


def numericify(n):
    """"""  # TODO
    if n is None:
        n = 0
    return n


def denominator(n):
    """"""  # TODO
    if n:
        return n
    else:
        return 1


def mean(numbers):
    """"""  # TODO
    if numbers and len(numbers) > 0:
        return statistics.mean(numbers)
    else:
        return 0


def remove_none_values(values):
    """"""  # TODO
    return [d for d in values if d is not None]


def log_error_if_check_failed(check_result, row, session_event, extra_message=None):
    if not check_result:
        message = 'Check failed: userID={}, trialType={} gameSessionID={} roundID={}, trialID={}'.format(
                            row['userId'],
                            session_event['trialType'],
                            session_event['gameSessionID'],
                            session_event['roundID'],
                            session_event['trialID'])
        if extra_message:
            message += ' ({})'.format(extra_message)
        logging.error(message, session_event)
