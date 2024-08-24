from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
import gymnasium as gym
from gymnasium import spaces
import logging
import numpy as np


logger = logging.getLogger(__name__)


def to_nparray(raw):
    wrapped_raw = list(raw)
    return np.array(wrapped_raw)


class FakeGymEnv(gym.Env):
    def __init__(self):
        super().__init__()
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
            low=np.zeros(7),
            high=np.ones(7),
            dtype=np.float64
        )
        self.seed()
        self.reset()

    def step(self, action):
        self.obs = np.random.random(7)
        reward = 0
        done = False
        info = {}
        return self.obs, reward, done, done, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.seed(seed)
        self.obs = np.zeros(7)
        return (self.obs, {})

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        return [seed]


def load_policy():
    logger.info(f"Creating new PPO policy")
    env = FakeGymEnv()
    model = PPO('MlpPolicy', env, verbose=1)

    # make function for producing an action given a single state
    def call_model(raw_state):
        obs = to_nparray(raw_state)
        actions = model.predict(obs)
        return actions
    return call_model


def main():

    env = FakeGymEnv()
    check_env(env)

    policy = load_policy()
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


# 0 nie rob nic
# 1 dodaj mala maszyne
# 2 dodaj srednia maszyne
# 3 dodaj duza maszyne
# 4 usun mala maszyne
# 5 usun srednia maszyne
# 6 usun duza maszyne


# 1. mozliwosc modyfikacji obserwacji na wejscie
# 2. tabelka/wykres - wizualizacja
# 3. statystyki - dystrybucja akcji
# 4. pokazanie historii
