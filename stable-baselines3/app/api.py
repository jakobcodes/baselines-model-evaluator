from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from waitress import serve
from load_policy_stable_baselines import load_policy
from db import StorageConfig
import datetime as dt
import logging
import base64
import time


app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s/%(name)s] %(message)s')

CORS(app, resources={r"/*": {"origins": "*"}})

storage_config = StorageConfig()
actions_storage = storage_config.actions_storage
policy_history_storage = storage_config.policy_history_storage
policy = load_policy()


@app.route('/ping', methods=['GET'])
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
            action, _ = policy(observation)
            logger.debug(f'Policy returned: {action}')

            result = {
                'status': 'ok',
                'obs': observation,
                'action': int(action),
                'datetime': dt.datetime.now().isoformat(),
            }
            actions_storage.save(result)
            return jsonify(result)

        return jsonify({
            'status': 'ok',
            'obs': req_as_json['obs'],
            'action': 0,
            'datetime': dt.datetime.now().isoformat(),
        })
    except Exception as e:
        logger.error('Unexpected exception caught, printing request details:')
        logger.error('Headers:')
        logger.error(request.headers)
        logger.error(f'Data: {request.data}')
        logger.exception(e)
        abort(500)


@app.route('/update', methods=['POST'])
def update_model():
    def is_valid_rq_update(req):
        if not req:
            return False

        for field in ['file_suffix', 'content']:
            if field not in req:
                return False

        return True

    global policy
    try:
        req_as_json = request.json
        if not is_valid_rq_update(req_as_json):
            logger.error(f'Request is not valid! Received text: '
                         f'{request.data.decode()}')
            abort(400)

        file_suffix = req_as_json['file_suffix']
        content = req_as_json['content']
        content_decoded = base64.b64decode(content)
        tstamp = int(time.time())

        if file_suffix != '':
            fname = f'{tstamp}_{file_suffix}.zip'
        else:
            fname = f'{tstamp}.zip'

        with open(fname, 'wb') as f:
            f.write(content_decoded)

        policy = load_policy(fname)

        policy_history_storage.save(fname.strip('.zip'))

        size = len(content_decoded)
        logger.debug(f'Store a new model: {fname} (size: {size})')
        return jsonify({
            'status': 'ok',
            'storage_path': fname,
            'size': size,
        })
    except Exception as e:
        logger.error('Unexpected exception caught, printing request details:')
        logger.error('Headers:')
        logger.error(request.headers)
        logger.error(f'Data: {request.data}')
        logger.exception(e)
        abort(500)


@app.route('/actions', methods=['GET'])
def get_actions_history():
    return jsonify(
        list(actions_storage.load())
    )

@app.route('/policies', methods=['GET'])
def get_policy_history():
    return jsonify(
        list(policy_history_storage.load())
    )


if __name__ == '__main__':
    serve(app, port=8080)
