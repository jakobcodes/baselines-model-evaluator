from flask import Flask, request, abort, jsonify
from baselinesme.load_policy import load_policy, DEFAULT_POLICY_PATH
import datetime as dt
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s/%(name)s] %(message)s')
app = Flask(__name__)

policy_path = os.environ.get('POLICY_PATH', DEFAULT_POLICY_PATH)
policy = load_policy(policy_path)


@app.route('/ping')
def ping():
    return f'PONG {dt.datetime.now()}'


def is_valid_request(req):
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
        if not is_valid_request(req_as_json):
            logger.error(f'Request is not valid! Received text: '
                         f'{request.data.decode()}')
            abort(400)

        observation = req_as_json['obs']
        logger.debug(f'Executing the policy with the state: {observation}')
        action = policy(observation)
        logger.debug(f'Policy returned: {action}')

        return jsonify({
            'status': 'ok',
            'input': req_as_json,
            'action': int(action),
        })
    except Exception as e:
        logger.error('Unexpected exception caught, printing request details:')
        logger.error('Headers:')
        logger.error(request.headers)
        logger.error(f'Data: {request.data}')
        logger.error(e)
        abort(500)


if __name__ == '__main__':
    app.run(debug=True)
