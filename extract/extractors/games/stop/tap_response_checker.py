import math

from utils import get_session_events, numericify


class TapResponseChecker:

    def __init__(self):
        pass

    def check_tap_responses(self, row):
        # trs = tap response start
        checks = {
            'GO': {
                'CORRECT_GO': lambda trs, session_event: trs > 0 and self.within_stimulus_boundary(session_event),
                'INCORRECT_GO': lambda trs, session_event: trs == 0,
                'MISS_GO': lambda trs, session_event: trs > 0 and self.outside_stimulus_boundary(session_event),
            },
            'STOP': {
                'CORRECT_STOP': lambda trs, session_event: trs == 0,
                'INCORRECT_STOP': lambda trs, session_event: trs > 0 and self.within_stimulus_boundary(session_event),
                'MISS_STOP': lambda trs, session_event: trs > 0 and self.outside_stimulus_boundary(session_event),
            }
        }
        session_events = get_session_events(row)
        for session_event in session_events:
            trial_type = session_event['trialType']
            tap_response_type = session_event['tapResponseType']
            tap_response_start = numericify(session_event['tapResponseStart'])
            check_result = checks[trial_type][tap_response_type](tap_response_start, session_event)
            if not check_result:
                prefix = 'tapResponsePosition'
                tx = float(session_event['{}X'.format(prefix)])
                ty = float(session_event['{}Y'.format(prefix)])
                ix = float(session_event['itemPositionX'])
                iy = float(session_event['itemPositionY'])
                print('\nCheck Failed:')
                print('      Game Session ID:', session_event['gameSessionID'])
                print('             Round ID:', session_event['roundID'])
                print('             Trial ID:', session_event['trialID'])
                print('           Trial Type:', trial_type)
                print('    Tap Response Type:', tap_response_type)
                print('   Tap Response Start:', tap_response_start, session_event['tapResponseStart'])
                print('Tap Response Position: ({},{})'.format(tx, ty))
                print('        Item Position: ({},{})'.format(ix, iy))
                print(tx, ty, ix, iy)
                # input('Press return to continue...')
            # assert check_result
            self.session_event_log.log_if_check_failed(check_result, session_event,
                                                       extra_message='tapResponseType={}'.format(tap_response_type))

    @staticmethod
    def within_stimulus_boundary(session_event, item_radius=95, prefix='tapResponsePosition'):
        tx = float(session_event['{}X'.format(prefix)])
        ty = float(session_event['{}Y'.format(prefix)])
        ix = float(session_event['itemPositionX'])
        iy = float(session_event['itemPositionY'])
        # print('\n', tx, ty, ix, iy)
        # return ((tx - ix) ** 2 + ((ty - iy) ** 2)) < (item_radius ** 2)
        distance = math.sqrt(((tx - ix) ** 2) + ((ty - iy) ** 2))
        print(distance, item_radius)
        return distance < item_radius

    def outside_stimulus_boundary(self, session_event, prefix='tapResponsePosition'):
        # print('within=', self.within_stimulus_boundary(session_event, prefix=prefix))
        return not self.within_stimulus_boundary(session_event, prefix=prefix)
