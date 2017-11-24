import socket
import select
import argparse
from flask import Flask, url_for

from flask import request
from flask import Response
from flask import json
from flask import jsonify

app = Flask(__name__)

# list of tasks
task_list = ['task1', 'task2', 'task3', 'task4', 'task5']

@app.route('/', methods=['GET'])
def get():

    if len(task_list) == 0:
        task = 'Done'
    else:
        task = task_list.pop(0)
        print("new length of task_list = ", len(task_list))

    data = {
        'task_number': task,
    }

    # resp = jsonify(task)
    # resp = Response(task, status=200, mimetype='text/plain')
    resp = jsonify(data)
    resp.status_code = 200
    return resp


@app.route('/', methods=['POST'])
def post():

    if request.headers['CONTENT_TYPE'] == 'application/json':

        data = request.json

        print("client status: ", data['status'])
        print("client cc: ", data['cc'])
        return "JSON Message: " + json.dumps(request.json)
    else:
        raise NotImplementedError


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='host ip of server.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='port of server.'
    )

    FLAGS, unparsed = parser.parse_known_args()

    # run application with set flags
    app.run(host=FLAGS.host, port=FLAGS.port)
