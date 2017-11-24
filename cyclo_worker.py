
import requests
import time
from random import *

def calculate_cyclomatic_complexity():
    """ calculate cyclomatic complexity """

    # For now simulate by waiting
    calc_time = randint(1, 4)
    time.sleep(calc_time)
    return calc_time


if __name__ == "__main__":

    client_id = randint(1, 100)
    client_name = 'client_{0}'.format(client_id)

    CycloServerAdress = "http://127.0.0.1:8000"

    while True:
        # ask the server for a task
        response = requests.get(CycloServerAdress)
        # task = response.text
        data = response.json()
        task = data['task_number']

        # if no task stop worker
        if task == 'Done':
            break

        # calculate cyclomatic complexity
        print('client {0} - calculating task {1}'.format(client_name, task))
        c = calculate_cyclomatic_complexity()

        stat_msg = '{} completed by client {}'.format(task, client_name)
        cc_msg = 'Complexity: {}'.format(c)

        post_msg = {'status': stat_msg, 'cc': cc_msg}

        # post result to the server
        # response = requests.post('http://127.0.0.1:8000', data='{}'.format(msg))
        response = requests.post('http://127.0.0.1:8000', json = post_msg)