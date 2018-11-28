from .tap_response_checker import TapResponseChecker

from utils import get_session_events, numericify, log_error_if_check_failed


class DoubleTapResponseChecker(TapResponseChecker):

    def __init__(self):
        pass

    def evaluate(self, row):
        self.check_tap_responses(row)

    def check_tap_responses(self, row):
        # trs is tap response start
        initial_tap_response_checks = {
            'GO': {
                'CORRECT_GO': lambda trs, session_event: trs > 0 and self.within_first_stimulus_boundary(session_event),
                'INCORRECT_GO': lambda trs, session_event: trs == 0,
                'MISS_GO': lambda trs, session_event: trs > 0 and self.outside_first_stimulus_boundary(session_event),
            },
            'DOUBLE': {
                'CORRECT': lambda trs, session_event: trs > 0 and self.within_first_stimulus_boundary(session_event),
                'INCORRECT': lambda trs, session_event: trs == 0,
                'MISS': lambda trs, session_event: trs > 0 and self.outside_first_stimulus_boundary(session_event),
            }
        }
        second_tap_response_checks = {
            'GO': {
                'N/A': lambda trs, session_event: trs == 0,
                'INCORRECT_DOUBLE_GO': lambda trs, session_event: trs > 0 and self.within_second_stimulus_boundary(session_event),
                'MISS_GO': lambda trs, session_event: trs > 0 and self.outside_second_stimulus_boundary(session_event),
                # Return True because no check is required
                'INCORR_DOUB_GO': lambda trs, session_event: True,
            },
            'DOUBLE': {
                'CORRECT': lambda trs, session_event: trs > 0 and self.within_second_stimulus_boundary(session_event),
                'INCORRECT': lambda trs, session_event: trs == 0,
                'MISS': lambda trs, session_event: trs > 0 and self.outside_second_stimulus_boundary(session_event),
            }
        }

        def check_tap_response(tap_response_checks, session_event, prefix):
            tap_response_type = session_event['{}TapResponseType'.format(prefix)]
            tap_response_start = numericify(session_event['{}TapResponseStart'.format(prefix)])
            # print(trial_type, tap_response_type)
            check_result = tap_response_checks[trial_type][tap_response_type](tap_response_start, session_event)
            # if not check_result:
            #     if prefix == 'initial':
            #         _prefix = 'initialTapResponsePosition'
            #     elif prefix == 'second':
            #         _prefix = 'secondTapResponsePosition'
            #     print('prefix', prefix)
            #     import json
            #     print(json.dumps(session_event))
            #     tx = float(session_event['{}X'.format(_prefix)])
            #     ty = float(session_event['{}Y'.format(_prefix)])
            #     ix = float(session_event['itemPositionX'])
            #     iy = float(session_event['itemPositionY'])
            #     print('\nCheck Failed:')
            #     print(type(check_result))
            #     print(trial_type)
            #     print(tap_response_type)
            #     if _prefix == 'initialTapResponsePosition':
            #         print(tap_response_start, session_event['initialTapResponseStart'])
            #     if _prefix == 'secondTapResponsePosition':
            #         print(tap_response_start, session_event['secondTapResponseStart'])
            #     print(tx, ty, ix, iy)
            #     # assert False
            log_error_if_check_failed(check_result, row, session_event,
                                      extra_message='tapResponseType={}'.format(tap_response_type))

        session_events = get_session_events(row)
        for session_event in session_events:
            trial_type = session_event['trialType']
            check_tap_response(initial_tap_response_checks, session_event, 'initial')
            check_tap_response(second_tap_response_checks, session_event, 'second')

    def within_first_stimulus_boundary(self, session_event):
        self.within_stimulus_boundary(session_event, prefix='initialTapResponsePosition')

    def outside_first_stimulus_boundary(self, session_event):
        self.outside_stimulus_boundary(session_event, prefix='initialTapResponsePosition')

    def within_second_stimulus_boundary(self, session_event):
        self.within_stimulus_boundary(session_event, prefix='secondTapResponsePosition')

    def outside_second_stimulus_boundary(self, session_event):
        self.outside_stimulus_boundary(session_event, prefix='secondTapResponsePosition')
