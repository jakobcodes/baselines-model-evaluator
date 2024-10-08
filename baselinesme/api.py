from flask import Flask, request, abort, jsonify
from baselinesme.load_policy import load_policy
import datetime as dt
import logging
import os
import time
import base64

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s/%(name)s] %(message)s')
app = Flask(__name__)
# 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


policy_storage_directory = os.environ.get('POLICY_STORAGE_DIRECTORY',
                                          '/srv/prod_policy')


def initialize_policy():
    initial_network_type = os.environ.get('INITIAL_NETWORK_TYPE')
    initial_policy_path = os.environ.get('INITIAL_POLICY_PATH')
    if initial_policy_path:
        return load_policy(fpath=initial_policy_path,
                           network_type=initial_network_type)

    return None

policy = initialize_policy()


@app.route('/ping')
def ping():
    return f'PONG {dt.datetime.now()}'


def is_valid_rq_oracle(req):
    if not req:
        return False

    logger.debug(f'Parsed JSON: {req}')

    if 'obs' not in req:
        return False

    return True


@app.route('/oracle', methods=['POST'])
def oracle():
    try:
        req_as_json = request.json
        if not is_valid_rq_oracle(req_as_json):
            logger.error(f'Request is not valid! Received text: '
                         f'{request.data.decode()}')
            abort(400)

        if policy:
            observation = req_as_json['obs']
            logger.debug(f'Executing the policy with the state: {observation}')
            action = policy(observation)
            logger.debug(f'Policy returned: {action}')

            return jsonify({
                'status': 'ok',
                'input': req_as_json,
                'action': int(action),
            })

        return jsonify({
            'status': 'ok',
            'input': req_as_json,
            'action': 0,
        })
    except Exception as e:
        logger.error('Unexpected exception caught, printing request details:')
        logger.error('Headers:')
        logger.error(request.headers)
        logger.error(f'Data: {request.data}')
        logger.exception(e)
        abort(500)


def is_valid_rq_update(req):
    if not req:
        return False

    for field in ['file_suffix', 'content', 'network_type']:
        if field not in req:
            return False

    return True


@app.route('/update', methods=['POST'])
def update_model():
    global policy
    try:
        req_as_json = request.json
        if not is_valid_rq_update(req_as_json):
            logger.error(f'Request is not valid! Received text: '
                         f'{request.data.decode()}')
            abort(400)

        file_suffix = req_as_json['file_suffix']
        network_type = req_as_json['network_type']
        content = req_as_json['content']
        content_decoded = base64.b64decode(content)
        tstamp = int(time.time())

        if file_suffix != '':
            fname = f'{tstamp}_{file_suffix}.bin'
        else:
            fname = f'{tstamp}.bin'

        policy_path = f'{policy_storage_directory}/{fname}'
        with open(policy_path, 'wb') as f:
            f.write(content_decoded)

        policy = load_policy(fpath=policy_path,
                             network_type=network_type)

        size = len(content_decoded)
        logger.debug(f'Store a new model: {policy_path} (size: {size})')
        return jsonify({
            'status': 'ok',
            'storage_path': policy_path,
            'size': size,
        })
    except Exception as e:
        logger.error('Unexpected exception caught, printing request details:')
        logger.error('Headers:')
        logger.error(request.headers)
        logger.error(f'Data: {request.data}')
        logger.exception(e)
        abort(500)

if __name__ == '__main__':
    app.run(debug=True)
