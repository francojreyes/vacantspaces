import signal
import sys
from json import dumps

from flask import Flask, request
from flask_cors import CORS

import backend
import config

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(
    __name__,
    static_url_path='/static/',
    static_folder='static'
)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/")
def index():
    with open("index.html") as FILE:
        page = FILE.read()

    return page


@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    return dumps({
        'data': data
    })


@APP.route("/vacantspaces", methods=['GET'])
def vacantspace():
    campus = request.args.get('campus')
    term = request.args.get('term')
    week = request.args.get('week')
    day = request.args.get('day')
    time = request.args.get('time')

    return dumps({
        'data': backend.vacantspaces(campus, term, week, day, time)
    })


@APP.route("/vacantspaces/now", methods=['GET'])
def vacantspace_now():
    campus = request.args.get('campus')

    return dumps({
        'data': backend.vacantspaces(campus, now=True)
    })

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
