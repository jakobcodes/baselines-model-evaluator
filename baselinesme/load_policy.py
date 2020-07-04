from baselines.ppo2.model import Model
from baselines.common.policies import build_policy
from baselines.common.tf_util import get_session
from gym import spaces

import joblib
import os.path as osp
import tensorflow as tf
import numpy as np
import sys
import logging

logger = logging.getLogger(__name__)


DEFAULT_POLICY_PATH = '/srv/prod_policy/model.bin'
DEFAULT_POLICY_NETWORK_TYPE = 'mlp'


def to_nparray(raw):
    wrapped_raw = list(raw)
    return np.array(wrapped_raw)


class FakeGymEnv:

    def __init__(self):
        self.action_space = spaces.Discrete(7)

        # observation metrics - all within 0-1 range
        # "vmAllocatedRatioHistory",
        # "avgCPUUtilizationHistory",
        # "p90CPUUtilizationHistory",
        # "avgMemoryUtilizationHistory",
        # "p90MemoryUtilizationHistory",
        # "waitingJobsRatioGlobalHistory",
        # "waitingJobsRatioRecentHistory"
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0]),
            high=np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        )


lstm_mask = np.zeros((1,))
lstm_state = None


def load_policy(fpath,
                network_type):
    global lstm_state

    fpath = fpath if fpath else DEFAULT_POLICY_PATH
    network_type = network_type if network_type else DEFAULT_POLICY_NETWORK_TYPE

    if network_type == 'test':
        return None

    logger.info(f"Loading policy from {fpath} with type {network_type}")
    env = FakeGymEnv()
    policy = build_policy(env, policy_network=network_type)

    model = Model(policy=policy,
                  ob_space=env.observation_space,
                  ac_space=env.action_space,
                  nbatch_act=1,
                  nbatch_train=1,  # not used
                  nsteps=1,  # not used
                  ent_coef=1,  # not used
                  vf_coef=1,  # not used
                  max_grad_norm=0.5,  # not used
                  mpi_rank_weight=1)
    model.load(fpath)
    lstm_state = model.initial_state if hasattr(model, 'initial_state') else None

    # make function for producing an action given a single state
    def call_model(raw_state):
        global lstm_state
        obs = to_nparray(raw_state)
        if lstm_state is not None:
            actions, _, lstm_state, _ = model.step(obs,
                                                   S=lstm_state,
                                                   M=lstm_mask)
        else:
            actions, _, _, _ = model.step(obs)
        return actions
    return call_model


def main():
    # observation metrics - all within 0-1 range
    # "vmAllocatedRatioHistory",
    # "avgCPUUtilizationHistory",
    # "p90CPUUtilizationHistory",
    # "avgMemoryUtilizationHistory",
    # "p90MemoryUtilizationHistory",
    # "waitingJobsRatioGlobalHistory",
    # "waitingJobsRatioRecentHistory"

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1:
        policy_path = sys.argv[1]
    else:
        policy_path = DEFAULT_POLICY_PATH

    logger.info(f'Path to the policy: {policy_path}')

    policy = load_policy(policy_path)
    state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    action = policy(state)
    print(f'Policy chose {action[0]}')
    action = policy(state)
    print(f'Policy chose {action[0]}')
    action = policy(state)
    print(f'Policy chose {action[0]}')
    action = policy(state)
    print(f'Policy chose {action[0]}')
    action = policy(state)
    print(f'Policy chose {action[0]}')


if __name__ == '__main__':
    main()
