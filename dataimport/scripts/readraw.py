import json
import pprint


class ReadRaw:
    def __init__(self):
        self.users = {}

    def open_file(self, filename):
        with open(filename, 'r') as file_handle:
            json_raw = json.load(file_handle)

            # print(pprint.pformat(json_raw))

            for row in json_raw[:100]:
                # print(pprint.pformat(row))

                if 'data' in row:

                    data_event = {}
                    data = row['data']
                    print('User ID', row['userId'])
                    print('Capture Date', row['captureDate'])

                    if 'bmi' in row['data']:
                        print('BMI', data['bmi'])
                        data_event['bmi'] = data['bmi']
                    if 'weight_kgs' in row['data']:
                        print('Weight KGs', data['weight_kgs'])
                        data_event['weight_kgs'] = data['weight_kgs']

                    if len(data_event.keys()):
                        if 'captureDate' in row:
                            print('BMI', row['captureDate'])
                            data_event['captureDate'] = row['captureDate']

                        if row['userId'] in self.users:
                            self.users[row['userId']].append(data_event)
                        else:
                            self.users[row['userId']] = [data_event]

                    # print(pprint.pformat(data))
                    print('\n')

        print(pprint.pformat(self.users))

        feedback = []

        for user in self.users.keys():
            individual_feedback = {}

            user_data = self.users[user]

            initial_bmi = float(user_data[0]['bmi'])
            recent_bmi = float(user_data[-1]['bmi'])

            print('User {} had Initial BMI of {}, now has {}'.format(user, initial_bmi, recent_bmi))
            individual_feedback['comment'] ='User {} had Initial BMI of {}, now has {}'.format(
                user, initial_bmi, recent_bmi
            )

            upper = initial_bmi * 1.1
            lower = initial_bmi * 0.9
            if recent_bmi < lower:
                print('Unhealthy user - too much weight loss')
                individual_feedback['error'] = 'Unhealthy user - too much weight loss'
            elif recent_bmi > upper:
                print('Unhealthy user - too much weight gain')
                individual_feedback['error'] = 'Unhealthy user - too much weight gain'
            else:
                print('User is within 10% of initial BMI')
                individual_feedback['ok'] = 'User is within 10% of initial BMI'

            print('\n')
            feedback.append(individual_feedback)

        return self.users, feedback


if __name__ == '__main__':
    rr = ReadRaw()

    filename = '../../091117.json'
    rr.open_file(filename=filename)
